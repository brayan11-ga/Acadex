import logging
import math
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.bloqueo_cuota_gemini import BloqueoCuotaGemini
from app.models.uso_analisis_ia import UsoAnalisisIA


logger = logging.getLogger(__name__)
RETENCION_DIAS = 30
ID_BLOQUEO_PROYECTO = "proyecto"
ZONA_REINICIO_GOOGLE = ZoneInfo("America/Los_Angeles")
MAXIMO_GRATUITO_POR_USUARIO = 1
MAXIMO_GRATUITO_POR_PROYECTO = 20


def _insertar_por_dialecto(db: Session):
    nombre_dialecto = db.get_bind().dialect.name
    if nombre_dialecto == "postgresql":
        return postgresql_insert
    if nombre_dialecto == "sqlite":
        return sqlite_insert
    raise RuntimeError("El control de uso de Gemini requiere PostgreSQL o SQLite")


def _incrementar_contador(
    db: Session,
    insertar,
    fecha_utc: date,
    alcance: str,
    identificador: str,
    limite: int,
) -> bool:
    tabla = UsoAnalisisIA.__table__
    sentencia = (
        insertar(tabla)
        .values(
            fecha_utc=fecha_utc,
            alcance=alcance,
            identificador_alcance=identificador,
            cantidad=1,
        )
        .on_conflict_do_update(
            index_elements=[
                tabla.c.fecha_utc,
                tabla.c.alcance,
                tabla.c.identificador_alcance,
            ],
            set_={"cantidad": tabla.c.cantidad + 1},
            where=tabla.c.cantidad < limite,
        )
        .returning(tabla.c.cantidad)
    )
    return db.execute(sentencia).scalar_one_or_none() is not None


def _ahora_utc(ahora: datetime | None = None) -> datetime:
    momento = ahora or datetime.now(timezone.utc)
    if momento.tzinfo is None:
        return momento.replace(tzinfo=timezone.utc)
    return momento.astimezone(timezone.utc)


def _fecha_cuota_google(ahora: datetime | None = None) -> date:
    return _ahora_utc(ahora).astimezone(ZONA_REINICIO_GOOGLE).date()


def proximo_reinicio_cuota_google(ahora: datetime | None = None) -> datetime:
    """Google reinicia RPD a medianoche del Pacífico; devolver ese instante en UTC."""
    momento_utc = _ahora_utc(ahora)
    ahora_pacifico = momento_utc.astimezone(ZONA_REINICIO_GOOGLE)
    siguiente_dia = ahora_pacifico.date() + timedelta(days=1)
    medianoche_pacifico = datetime.combine(
        siguiente_dia, time.min, tzinfo=ZONA_REINICIO_GOOGLE
    )
    return medianoche_pacifico.astimezone(timezone.utc)


def _normalizar_utc(valor: datetime) -> datetime:
    # SQLite devuelve como naive los DateTime almacenados aunque la columna
    # declare timezone=True; en esta tabla todos los valores se escriben en UTC.
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def verificar_bloqueo_cuota_google(
    db: Session, *, ahora: datetime | None = None
) -> None:
    """Evita nuevas llamadas mientras siga agotada la cuota diaria del proyecto."""
    momento_utc = _ahora_utc(ahora)
    try:
        bloqueo = db.get(BloqueoCuotaGemini, ID_BLOQUEO_PROYECTO)
        if bloqueo is None:
            return

        bloqueado_hasta = _normalizar_utc(bloqueo.bloqueado_hasta)
        if momento_utc >= bloqueado_hasta:
            return

        espera = max(1, math.ceil((bloqueado_hasta - momento_utc).total_seconds()))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Se agotó la cuota gratuita diaria de Google para la demostración. "
                "El análisis volverá a estar disponible después del reinicio diario."
            ),
            headers={"Retry-After": str(espera)},
        )
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.warning("No se pudo consultar el bloqueo diario de Gemini")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de IA no está disponible en este momento.",
        ) from None


def bloquear_hasta_reinicio_cuota_google(
    db: Session, *, ahora: datetime | None = None
) -> datetime:
    """Guarda un bloqueo del proyecto compartido hasta medianoche del Pacífico."""
    bloqueado_hasta = proximo_reinicio_cuota_google(ahora)
    tabla = BloqueoCuotaGemini.__table__

    try:
        insertar = _insertar_por_dialecto(db)
        nuevo_bloqueo = insertar(tabla)
        sentencia = (
            nuevo_bloqueo
            .values(id=ID_BLOQUEO_PROYECTO, bloqueado_hasta=bloqueado_hasta)
            .on_conflict_do_update(
                index_elements=[tabla.c.id],
                set_={
                    "bloqueado_hasta": nuevo_bloqueo.excluded.bloqueado_hasta
                },
                where=(
                    tabla.c.bloqueado_hasta
                    < nuevo_bloqueo.excluded.bloqueado_hasta
                ),
            )
        )
        db.execute(sentencia)
        db.commit()
        return bloqueado_hasta
    except (SQLAlchemyError, RuntimeError):
        db.rollback()
        logger.warning("No se pudo guardar el bloqueo diario de Gemini")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de IA no está disponible en este momento.",
        ) from None


def consumir_cupo_analisis(
    db: Session,
    id_usuario: int,
    *,
    fecha_utc: date | None = None,
    fecha_global: date | None = None,
    limite_usuario: int | None = None,
    limite_global: int | None = None,
) -> None:
    """Reserva un uso diario por usuario y uno global en una transacción atómica."""
    if not isinstance(id_usuario, int) or id_usuario <= 0:
        raise ValueError("Se requiere un usuario autenticado para consumir Gemini")

    momento = datetime.now(timezone.utc)
    hoy_utc = fecha_utc or momento.date()
    # La cuota global usa el mismo día de reinicio que Google. fecha_utc permite
    # fijar ambas fechas en las pruebas sin cambiar el reloj del proceso.
    dia_global = fecha_global or (
        fecha_utc if fecha_utc is not None else _fecha_cuota_google(momento)
    )
    maximo_usuario = (
        min(settings.gemini_user_daily_limit, MAXIMO_GRATUITO_POR_USUARIO)
        if limite_usuario is None
        else limite_usuario
    )
    maximo_global = (
        min(settings.gemini_global_daily_limit, MAXIMO_GRATUITO_POR_PROYECTO)
        if limite_global is None
        else limite_global
    )

    try:
        insertar = _insertar_por_dialecto(db)
        db.execute(
            delete(UsoAnalisisIA).where(
                UsoAnalisisIA.fecha_utc < hoy_utc - timedelta(days=RETENCION_DIAS)
            )
        )

        if not _incrementar_contador(
            db, insertar, hoy_utc, "usuario", str(id_usuario), maximo_usuario
        ):
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Alcanzaste el límite de {maximo_usuario} análisis de IA por día.",
            )

        if not _incrementar_contador(
            db, insertar, dia_global, "global", "global", maximo_global
        ):
            db.rollback()
            segundos_hasta_reinicio = max(
                1,
                math.ceil(
                    (
                        proximo_reinicio_cuota_google()
                        - datetime.now(timezone.utc)
                    ).total_seconds()
                ),
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Se alcanzó el límite diario de análisis de IA de la demostración.",
                headers={"Retry-After": str(segundos_hasta_reinicio)},
            )

        db.commit()
    except HTTPException:
        raise
    except (SQLAlchemyError, RuntimeError):
        db.rollback()
        logger.warning("No se pudo reservar el cupo diario de análisis de IA")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de IA no está disponible en este momento.",
        ) from None


def liberar_cupo_usuario_analisis(
    db: Session, id_usuario: int, *, fecha_utc: date | None = None
) -> None:
    """Permite reintentar en otro momento si Google rechazó la llamada."""
    hoy_utc = fecha_utc or datetime.now(timezone.utc).date()
    try:
        tabla = UsoAnalisisIA.__table__
        db.execute(
            tabla.update()
            .where(
                tabla.c.fecha_utc == hoy_utc,
                tabla.c.alcance == "usuario",
                tabla.c.identificador_alcance == str(id_usuario),
                tabla.c.cantidad > 0,
            )
            .values(cantidad=tabla.c.cantidad - 1)
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        # El contador global no se libera: cada intento sigue consumiendo la
        # reserva de seguridad de la cuota gratuita del proyecto.
        logger.warning("No se pudo liberar el cupo personal tras un error de Gemini")
