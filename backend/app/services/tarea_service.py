# Ruta: backend/app/services/tarea_service.py
import logging
from datetime import date, datetime
from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.models.tarea import Tarea
from app.models.historial_tarea import HistorialTarea
from app.repositories import tarea_repository
from app.schemas.tarea import TareaCreate, TareaUpdate
from app.repositories import asignacion_tarea_repository, grupo_repository
from app.repositories import archivo_repository
from app.repositories import historial_tarea_repository, sesion_cronometro_repository
from app.repositories import notificacion_repository
from app.schemas.tarea import TareaGrupalCreate
from app.config.settings import MAX_ARCHIVOS_POR_TAREA
from app.models.usuario import Usuario
from app.services import archivo_service

logger = logging.getLogger(__name__)


def _es_lider(db: Session, id_usuario: int, id_grupo: int) -> bool:
    integrante = grupo_repository.obtener_integrante(db, id_usuario, id_grupo)
    return integrante is not None and integrante.rol == "lider"


def _recortar_nombre_tarea(nombre: str, maximo: int = 35) -> str:
    """Recorta el nombre para que quepa en el detalle de una notificación."""
    texto = (nombre or "").strip()
    if len(texto) <= maximo:
        return texto
    return texto[: maximo - 1].rstrip() + "…"


_MESES_CORTOS = {
    1: "ene.",
    2: "feb.",
    3: "mar.",
    4: "abr.",
    5: "may.",
    6: "jun.",
    7: "jul.",
    8: "ago.",
    9: "sep.",
    10: "oct.",
    11: "nov.",
    12: "dic.",
}


def _formatear_fecha_corta(fecha: Optional[datetime]) -> str:
    """Devuelve una fecha breve en español, por ejemplo "30 oct."."""
    if fecha is None:
        return ""
    return f"{fecha.day} {_MESES_CORTOS.get(fecha.month, '')}".strip()


def _calcular_estado_grupal(
    tarea: Tarea, ids_asignados: set[int], ids_completados: set[int]
) -> str:
    """Regla de C3: completada solo si todos los asignados tienen historial."""
    if ids_asignados and ids_asignados.issubset(ids_completados):
        return "Completada"
    if (tarea.estado or "").lower() == "pendiente":
        return "en progreso"
    return tarea.estado


def _notificar(
    db: Session,
    *,
    titulo: str,
    detalles: str,
    tipo: str,
    id_usuario: int,
    id_tarea: int,
) -> None:
    """Crea una notificación sin tumbar la operación principal si falla.

    Se llama después del commit de reabrir/reasignar: un fallo aquí solo se
    registra en el log y no deshace el cambio de la tarea.
    """
    try:
        notificacion_repository.crear_notificacion(
            db,
            titulo=titulo[:50],
            detalles=detalles[:100],
            tipo=tipo,
            id_usuario=id_usuario,
            id_tarea=id_tarea,
        )
    except Exception:
        db.rollback()
        logger.exception(
            "No se pudo crear la notificación %s para el usuario %s",
            tipo,
            id_usuario,
        )


def crear_tarea(db: Session, datos: TareaCreate, usuario: Usuario, *, commit: bool = True) -> Tarea:
    if datos.id_grupo is None:
        datos_seguridad = datos.model_copy(update={"id_usuario": usuario.id_usuario})
    else:
        if not getattr(usuario, "es_admin", False) and not _es_lider(
            db, usuario.id_usuario, datos.id_grupo
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para crear tareas en este grupo.",
            )
        datos_seguridad = datos.model_copy(update={"id_usuario": None})
    return tarea_repository.crear_tarea(db, datos_seguridad, commit=commit)


def crear_tarea_con_pdf(
    db: Session,
    datos: TareaCreate,
    usuario: Usuario,
    archivo_pdf: UploadFile,
) -> Tarea:
    """Guarda la tarea y su PDF en una sola transacción de PostgreSQL."""
    if datos.id_grupo is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este guardado con PDF está disponible para tareas personales.",
        )

    try:
        with archivo_service.compensar_subidas_adjuntos() as recursos_creados:
            tarea = crear_tarea(db, datos, usuario, commit=False)
            archivo_service.subir_archivo_tarea(
                db,
                tarea.id_tarea,
                archivo_pdf,
                usuario.id_usuario,
                commit=False,
                recursos_creados=recursos_creados,
            )
            db.commit()
    except Exception:
        db.rollback()
        raise

    return tarea

def obtener_tarea(db: Session, id_tarea: int, id_usuario: int) -> Tarea:
    tarea = tarea_repository.obtener_tarea_por_id(db, id_tarea)
    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    if tarea.id_usuario is not None:
        autorizado = tarea.id_usuario == id_usuario
    else:
        autorizado = grupo_repository.obtener_integrante(db, id_usuario, tarea.id_grupo) is not None
    if not autorizado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta tarea.",
        )
    if db is not None:
        tarea.total_archivos = archivo_repository.contar_archivos_de_tarea(db, tarea.id_tarea)
    return tarea

def _adjuntar_total_archivos(db: Session, tareas: List[Tarea]) -> List[Tarea]:
    # Una sola consulta agrupada rellena total_archivos en todas las tareas (sin N+1).
    if db is None or not tareas:
        return tareas
    conteos = archivo_repository.obtener_conteo_archivos_por_tareas(
        db, [tarea.id_tarea for tarea in tareas]
    )
    for tarea in tareas:
        tarea.total_archivos = conteos.get(tarea.id_tarea, 0)
    return tareas


def listar_tareas(db: Session, id_usuario: int) -> List[Tarea]:
    return _adjuntar_total_archivos(
        db, tarea_repository.obtener_tareas_visibles_para_usuario(db, id_usuario)
    )

def actualizar_tarea(db: Session, id_tarea: int, datos: TareaUpdate, id_usuario: int) -> Tarea:
    tarea = obtener_tarea(db, id_tarea, id_usuario)
    cambios = datos.model_dump(exclude_unset=True)
    if tarea.id_grupo is not None:
        # En las tareas grupales solo el líder edita, y solo mientras no esté
        # completada. El estado lo mueve únicamente "Completar mi parte".
        if not _es_lider(db, id_usuario, tarea.id_grupo):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para modificar esta tarea.",
            )
        if (tarea.estado or "").lower() == "completada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reábrila primero.",
            )
        if "estado" in cambios:
            estado_nuevo = cambios["estado"]
            if estado_nuevo is not None and estado_nuevo.lower() == "completada":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usa Completar mi parte.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No puedes cambiar el estado de una tarea grupal; "
                    "se actualiza al completar cada parte."
                ),
            )
    if cambios.get("max_archivos") is not None:
        nuevo_max = cambios["max_archivos"]
        if tarea.id_grupo is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las tareas individuales no permiten definir un máximo de archivos.",
            )
        if nuevo_max > MAX_ARCHIVOS_POR_TAREA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El máximo permitido por el sistema es {MAX_ARCHIVOS_POR_TAREA}.",
            )
        total_actual = archivo_repository.contar_archivos_de_tarea(db, tarea.id_tarea)
        if nuevo_max < total_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"No puedes fijar el máximo en {nuevo_max}: "
                    f"la tarea ya tiene {total_actual} archivos."
                ),
            )
    estado_anterior = tarea.estado

    # Actualizamos la tarea mediante el repositorio
    try:
        tarea_actualizada = tarea_repository.actualizar_tarea(
            db, tarea, datos, commit=False
        )
        estado_nuevo = tarea_actualizada.estado

        # Tarea, historial y estadística se confirman en un único commit.
        id_usuario_historial = tarea_actualizada.id_usuario or id_usuario
        if (
            tarea_actualizada.id_grupo is None
            and estado_nuevo
            and estado_anterior
            and estado_nuevo.lower() == "completada"
            and estado_anterior.lower() != "completada"
        ):
            db.add(
                HistorialTarea(
                    id_tarea=tarea_actualizada.id_tarea,
                    id_usuario=id_usuario_historial,
                    id_grupo=tarea_actualizada.id_grupo,
                    fechahora_fin=datetime.now(),
                    tiempo_real=tarea_actualizada.tiempo_acumulado,
                    dificultad_real=tarea_actualizada.dificultad_estimada,
                )
            )
            if db is not None:
                db.flush()

            from app.services import estadistica_service

            estadistica_service.recalcular_estadistica_categoria(
                db,
                id_usuario_historial,
                tarea_actualizada.id_categoria,
                commit=False,
            )

        # Reabrir conserva el historial como evidencia de una finalización
        # anterior. Si vuelve a completarse se agrega un nuevo registro.
        if db is not None:
            db.commit()
            db.refresh(tarea_actualizada)
        return tarea_actualizada
    except Exception:
        if db is not None:
            db.rollback()
        raise

def completar_parte_tarea(
    db: Session, id_tarea: int, dificultad_real: int, id_usuario: int
) -> Tarea:
    """Registra la parte de un asignado en una tarea grupal.

    El estado de la tarea se mueve solo aquí: pasa a "Completada" cuando todos
    los asignados ya registraron su parte.
    """
    tarea = tarea_repository.obtener_tarea_por_id(db, id_tarea)
    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    if tarea.id_grupo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta tarea no es grupal; usa el flujo actual (PUT).",
        )
    if not asignacion_tarea_repository.usuario_tiene_asignacion(
        db, id_tarea, id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un integrante asignado puede completar su parte de esta tarea.",
        )
    if (tarea.estado or "").lower() == "completada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La tarea ya está completada.",
        )
    if historial_tarea_repository.usuario_ya_completo(db, id_tarea, id_usuario):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya completaste tu parte de esta tarea.",
        )
    if sesion_cronometro_repository.get_sesion_activa_de_usuario(
        db, id_tarea, id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pausa tu cronómetro antes de completar tu parte.",
        )

    # Tiempo real = segundos de las sesiones CERRADAS de este usuario en esta tarea.
    tiempo_real = sesion_cronometro_repository.sumar_duracion_cerrada(
        db, id_tarea, id_usuario
    )

    try:
        historial_tarea_repository.upsert(
            db,
            id_tarea=id_tarea,
            id_usuario=id_usuario,
            id_grupo=tarea.id_grupo,
            dificultad_real=dificultad_real,
            tiempo_real=tiempo_real,
            commit=False,
        )

        # Todos los asignados deben tener fila para marcar la tarea como completada.
        asignados = asignacion_tarea_repository.obtener_usuarios_asignados(db, id_tarea)
        completados = historial_tarea_repository.obtener_usuarios_completados(db, id_tarea)
        ids_asignados = {usuario.id_usuario for usuario in asignados}
        tarea.estado = _calcular_estado_grupal(tarea, ids_asignados, completados)

        db.commit()
        db.refresh(tarea)
        tarea.total_archivos = archivo_repository.contar_archivos_de_tarea(db, id_tarea)
        return tarea
    except Exception:
        db.rollback()
        raise

def reabrir_tarea_grupal(db: Session, id_tarea: int, id_usuario: int) -> Tarea:
    """Devuelve a "en progreso" una tarea grupal que estaba "Completada" (C4b).

    Solo el líder puede hacerlo. Borra todo el historial de la tarea, pero
    conserva archivos, sesiones, asignaciones y datos de la tarea. No recalcula
    estadísticas: es una decisión explícita de C4b.
    """
    tarea = tarea_repository.obtener_tarea_por_id(db, id_tarea)
    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    if tarea.id_grupo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta tarea no es grupal; usa el flujo actual (PUT).",
        )
    if not _es_lider(db, id_usuario, tarea.id_grupo):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el líder del grupo puede reabrir esta tarea.",
        )
    if (tarea.estado or "").lower() != "completada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La tarea no está completada.",
        )

    try:
        historial_tarea_repository.eliminar_por_tarea(db, id_tarea)
        tarea.estado = "en progreso"
        db.commit()
        db.refresh(tarea)
    except Exception:
        db.rollback()
        raise

    # Las notificaciones se crean después del commit: si una falla, la tarea
    # ya quedó reabierta y el error solo se registra en el log.
    try:
        nombre = _recortar_nombre_tarea(tarea.nombre)
        asignados = asignacion_tarea_repository.obtener_usuarios_asignados(db, id_tarea)
        for asignado in asignados:
            if asignado.id_usuario == id_usuario:
                continue
            _notificar(
                db,
                titulo="Una tarea volvió a estar en progreso",
                detalles=(
                    f"El líder reabrió «{nombre}». "
                    "Debes completar tu parte otra vez."
                ),
                tipo="tarea_reabierta",
                id_usuario=asignado.id_usuario,
                id_tarea=id_tarea,
            )
    except Exception:
        db.rollback()
        logger.exception("No se pudieron crear las notificaciones de la reapertura")

    tarea.total_archivos = archivo_repository.contar_archivos_de_tarea(db, id_tarea)
    return tarea


def reasignar_asignados_tarea(
    db: Session, id_tarea: int, ids_usuarios: List[int], id_usuario: int
) -> Tarea:
    """Reemplaza el conjunto completo de asignados de una tarea grupal (C4c).

    Solo el líder puede hacerlo mientras la tarea no esté completada. Al quitar
    a alguien se borra solo su avance en esa tarea (archivos propios, sesiones,
    historial y asignación). No recalcula estadísticas.
    """
    tarea = tarea_repository.obtener_tarea_por_id(db, id_tarea)
    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    if tarea.id_grupo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta tarea no es grupal; usa el flujo actual (PUT).",
        )
    if not _es_lider(db, id_usuario, tarea.id_grupo):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el líder del grupo puede reasignar esta tarea.",
        )
    if (tarea.estado or "").lower() == "completada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Reábrela primero.",
        )
    if not ids_usuarios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La tarea debe tener al menos un asignado.",
        )
    if len(set(ids_usuarios)) != len(ids_usuarios):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se permiten asignados repetidos.",
        )

    integrantes_por_usuario = {}
    for id_destino in ids_usuarios:
        integrante = grupo_repository.obtener_integrante(
            db, id_destino, tarea.id_grupo
        )
        if integrante is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Todos los asignados deben pertenecer a este grupo.",
            )
        integrantes_por_usuario[id_destino] = integrante

    actuales = asignacion_tarea_repository.obtener_usuarios_asignados(db, id_tarea)
    ids_actuales = {usuario.id_usuario for usuario in actuales}
    ids_nuevos = set(ids_usuarios)
    if ids_actuales == ids_nuevos:
        # Mismo conjunto: 200 sin cambios ni notificaciones.
        tarea.total_archivos = archivo_repository.contar_archivos_de_tarea(
            db, id_tarea
        )
        return tarea

    ids_quitados = sorted(ids_actuales - ids_nuevos)
    ids_agregados = sorted(ids_nuevos - ids_actuales)

    # Se calcula antes de borrar para decidir el texto de la notificación.
    trabajo_por_usuario = {}
    for id_quitado in ids_quitados:
        tiene_archivos = bool(
            archivo_repository.obtener_archivos_de_usuarios_en_tarea(
                db, id_tarea, [id_quitado]
            )
        )
        sesiones = sesion_cronometro_repository.obtener_sesiones_de_usuario_en_tarea(
            db, id_tarea, id_quitado
        )
        tiene_tiempo = any(
            (sesion.duracion or 0) > 0 or sesion.fecha_fin is None
            for sesion in sesiones
        )
        tiene_historial = (
            historial_tarea_repository.obtener_fila(db, id_quitado, id_tarea)
            is not None
        )
        trabajo_por_usuario[id_quitado] = (
            tiene_archivos or tiene_tiempo or tiene_historial
        )

    nombre = _recortar_nombre_tarea(tarea.nombre)
    fecha = _formatear_fecha_corta(tarea.fecha_entrega)
    id_grupo = tarea.id_grupo

    try:
        with archivo_service.preparar_eliminacion_archivos_usuarios_tarea(
            db, id_tarea, ids_quitados
        ):
            archivo_repository.eliminar_archivos_de_usuarios_en_tarea(
                db, id_tarea, ids_quitados
            )
            for id_quitado in ids_quitados:
                sesion_cronometro_repository.eliminar_sesiones_de_usuario_en_tarea(
                    db, id_tarea, id_quitado
                )
                historial_tarea_repository.eliminar_por_usuario_y_tarea(
                    db, id_tarea, id_quitado
                )
                integrante_quitado = grupo_repository.obtener_integrante(
                    db, id_quitado, id_grupo
                )
                if integrante_quitado is not None:
                    asignacion_tarea_repository.eliminar_por_tarea_e_integrante(
                        db, id_tarea, integrante_quitado.id_integrante
                    )

            for id_agregado in ids_agregados:
                asignacion_tarea_repository.crear_asignacion(
                    db,
                    id_tarea,
                    integrantes_por_usuario[id_agregado].id_integrante,
                    commit=False,
                )

            # La regla de estado es la misma de "Completar mi parte" (C3).
            asignados = asignacion_tarea_repository.obtener_usuarios_asignados(
                db, id_tarea
            )
            completados = historial_tarea_repository.obtener_usuarios_completados(
                db, id_tarea
            )
            ids_asignados = {usuario.id_usuario for usuario in asignados}
            tarea.estado = _calcular_estado_grupal(
                tarea, ids_asignados, completados
            )

            db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(tarea)

    # Notificaciones después del commit: un fallo no deshace la reasignación.
    for id_agregado in ids_agregados:
        _notificar(
            db,
            titulo="Tienes una tarea nueva",
            detalles=f"El líder te asignó «{nombre}». Entrega: {fecha}",
            tipo="tarea_asignada",
            id_usuario=id_agregado,
            id_tarea=id_tarea,
        )
    for id_quitado in ids_quitados:
        if trabajo_por_usuario[id_quitado]:
            detalle = (
                f"El líder te quitó de «{nombre}». "
                "Se borraron tus archivos y tu tiempo."
            )
        else:
            detalle = f"El líder te quitó de «{nombre}»."
        _notificar(
            db,
            titulo="Ya no estás asignado a una tarea",
            detalles=detalle,
            tipo="tarea_retirada",
            id_usuario=id_quitado,
            id_tarea=id_tarea,
        )

    tarea.total_archivos = archivo_repository.contar_archivos_de_tarea(db, id_tarea)
    return tarea


def eliminar_tarea(db: Session, id_tarea: int, id_usuario: int) -> None:
    tarea = obtener_tarea(db, id_tarea, id_usuario)
    if tarea.id_usuario is not None:
        autorizado = tarea.id_usuario == id_usuario
    else:
        integrante = grupo_repository.obtener_integrante(db, id_usuario, tarea.id_grupo)
        autorizado = integrante is not None and integrante.rol == "lider"

    if not autorizado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta tarea.",
        )

    # Mantiene los binarios recuperables si falla el commit que elimina la tarea y sus metadatos.
    with archivo_service.preparar_eliminacion_archivos_tarea(db, id_tarea):
        tarea_repository.eliminar_tarea(db, tarea)

def listar_tareas_calendario(
    db: Session,
    desde: date,
    hasta: date,
    id_usuario_actual: int,
    id_usuario: Optional[int],
    id_grupo: Optional[int] = None,
) -> List[Tarea]:
    if id_usuario is not None and id_usuario != id_usuario_actual:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar las tareas de este usuario.",
        )
    if id_grupo is not None and grupo_repository.obtener_integrante(
        db, id_usuario_actual, id_grupo
    ) is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar las tareas de este grupo.",
        )
    return _adjuntar_total_archivos(
        db,
        tarea_repository.obtener_tareas_por_rango(
            db, desde, hasta, id_usuario_actual, id_grupo
        ),
    )

def crear_tarea_grupal(
    db: Session, id_grupo: int, datos: TareaGrupalCreate, usuario: Usuario
) -> Tarea:
    if not getattr(usuario, "es_admin", False) and not _es_lider(
        db, usuario.id_usuario, id_grupo
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de líder sobre este grupo.",
        )

    if not datos.ids_usuarios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La tarea debe tener al menos un asignado.",
        )
    if len(set(datos.ids_usuarios)) != len(datos.ids_usuarios):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se permiten asignados repetidos.",
        )

    integrantes = []
    for id_usuario in datos.ids_usuarios:
        integrante = grupo_repository.obtener_integrante(db, id_usuario, id_grupo)
        if not integrante:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Todos los asignados deben pertenecer a este grupo.",
            )
        integrantes.append(integrante)

    tarea_datos = TareaCreate(
        nombre=datos.nombre,
        descripcion=datos.descripcion,
        fecha_entrega=datos.fecha_entrega,
        dificultad_estimada=datos.dificultad_estimada,
        tiempo_estimado=datos.tiempo_estimado,
        id_categoria=datos.id_categoria,
        id_usuario=None,
        id_grupo=id_grupo,
    )
    # Se captura antes del commit: después, los Integrante quedan expirados.
    destinatarios = [
        (integrante.id_usuario, integrante.rol) for integrante in integrantes
    ]

    try:
        tarea = tarea_repository.crear_tarea(
            db, tarea_datos, commit=False, max_archivos=datos.max_archivos
        )

        for integrante in integrantes:
            asignacion_tarea_repository.crear_asignacion(
                db, tarea.id_tarea, integrante.id_integrante, commit=False
            )

        db.commit()
        db.refresh(tarea)
    except Exception:
        db.rollback()
        raise

    # Aviso a los asignados, excepto al líder del grupo.
    nombre = _recortar_nombre_tarea(tarea.nombre)
    fecha = _formatear_fecha_corta(tarea.fecha_entrega)
    for id_destinatario, rol in destinatarios:
        if rol == "lider":
            continue
        _notificar(
            db,
            titulo="Tienes una tarea nueva",
            detalles=f"El líder te asignó «{nombre}». Entrega: {fecha}",
            tipo="tarea_asignada",
            id_usuario=id_destinatario,
            id_tarea=tarea.id_tarea,
        )

    return tarea

def listar_tareas_asignadas(db: Session, id_usuario: int) -> List[Tarea]:
    return _adjuntar_total_archivos(
        db, asignacion_tarea_repository.obtener_tareas_asignadas_a_usuario(db, id_usuario)
    )

def listar_tareas_de_grupo(db: Session, id_grupo: int, id_usuario: int) -> List[Tarea]:
    if grupo_repository.obtener_integrante(db, id_usuario, id_grupo) is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar las tareas de este grupo.",
        )
    return _adjuntar_total_archivos(
        db, tarea_repository.obtener_tareas_por_grupo(db, id_grupo)
    )

def listar_asignados_de_tarea(db: Session, id_tarea: int, id_usuario: int) -> List[dict]:
    # obtener_tarea ya valida el acceso: dueño en las individuales y miembro del grupo
    # en las grupales. Cualquier miembro del grupo puede ver los asignados (RF-045).
    tarea = obtener_tarea(db, id_tarea, id_usuario)
    usuarios = asignacion_tarea_repository.obtener_usuarios_asignados(db, tarea.id_tarea)
    # Una sola consulta trae quiénes ya completaron su parte (sin N+1).
    completados = historial_tarea_repository.obtener_usuarios_completados(db, tarea.id_tarea)
    return [
        {
            "id_usuario": usuario.id_usuario,
            "correo_electronico": usuario.correo_electronico,
            "completado": usuario.id_usuario in completados,
        }
        for usuario in usuarios
    ]

def verificar_permiso_tarea(
    db: Session, id_tarea: int, id_usuario: int, accion: str
) -> Tarea:
    tarea = tarea_repository.obtener_tarea_por_id(db, id_tarea)
    if tarea is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    if tarea.id_usuario is not None:
        autorizado = tarea.id_usuario == id_usuario
    elif accion == "cronometro":
        autorizado = asignacion_tarea_repository.usuario_tiene_asignacion(
            db, tarea.id_tarea, id_usuario
        )
    else:
        autorizado = grupo_repository.obtener_integrante(db, id_usuario, tarea.id_grupo) is not None
    if not autorizado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta tarea.",
        )
    return tarea
