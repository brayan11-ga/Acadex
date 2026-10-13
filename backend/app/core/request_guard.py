import hashlib
import hmac
import logging
import math
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import case, delete, or_, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.limite_solicitud import LimiteSolicitud


logger = logging.getLogger(__name__)
RETENCION_SEGUNDOS = 24 * 60 * 60


def _clave_hash(alcance: str, identificador: str) -> str:
    mensaje = f"{alcance}:{identificador.strip().lower() or 'desconocido'}".encode("utf-8")
    return hmac.new(settings.secret_key.encode("utf-8"), mensaje, hashlib.sha256).hexdigest()


def limitar_solicitudes(
    db: Session,
    alcance: str,
    identificador: str,
    *,
    maximo: int,
    ventana_segundos: int,
    mensaje: str = "Has realizado demasiadas solicitudes. Inténtalo de nuevo más tarde.",
) -> None:
    """Consume un límite fijo compartido entre instancias mediante PostgreSQL/SQLite."""
    if maximo < 1 or ventana_segundos < 1:
        raise ValueError("El límite y la ventana deben ser positivos")

    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    inicio_minimo = ahora - timedelta(seconds=ventana_segundos)
    clave = _clave_hash(alcance, identificador)
    tabla = LimiteSolicitud.__table__
    dialecto = db.get_bind().dialect.name
    insertar = {
        "postgresql": postgresql_insert,
        "sqlite": sqlite_insert,
    }.get(dialecto)
    if insertar is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La protección temporal no está disponible.",
        )

    ventana_expirada = tabla.c.inicio_ventana <= inicio_minimo
    sentencia = (
        insertar(tabla)
        .values(
            alcance=alcance,
            clave_hash=clave,
            inicio_ventana=ahora,
            cantidad=1,
        )
        .on_conflict_do_update(
            index_elements=[tabla.c.alcance, tabla.c.clave_hash],
            set_={
                "inicio_ventana": case((ventana_expirada, ahora), else_=tabla.c.inicio_ventana),
                "cantidad": case((ventana_expirada, 1), else_=tabla.c.cantidad + 1),
            },
            where=or_(ventana_expirada, tabla.c.cantidad < maximo),
        )
        .returning(tabla.c.cantidad)
    )

    try:
        cantidad = db.execute(sentencia).scalar_one_or_none()
        if cantidad is None:
            inicio = db.execute(
                select(tabla.c.inicio_ventana).where(
                    tabla.c.alcance == alcance,
                    tabla.c.clave_hash == clave,
                )
            ).scalar_one()
            db.rollback()
            espera = max(
                1,
                math.ceil(
                    (
                        inicio + timedelta(seconds=ventana_segundos) - ahora
                    ).total_seconds()
                ),
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=mensaje,
                headers={"Retry-After": str(espera)},
            )

        db.execute(
            delete(LimiteSolicitud).where(
                LimiteSolicitud.inicio_ventana < ahora - timedelta(seconds=RETENCION_SEGUNDOS)
            )
        )
        db.commit()
    except HTTPException:
        raise
    except (SQLAlchemyError, RuntimeError):
        db.rollback()
        logger.warning("No se pudo aplicar el límite temporal de solicitudes")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La protección temporal no está disponible.",
        ) from None
