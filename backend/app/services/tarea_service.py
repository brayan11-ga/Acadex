# Ruta: backend/app/services/tarea_service.py
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
from app.schemas.tarea import TareaGrupalCreate
from app.config.settings import MAX_ARCHIVOS_POR_TAREA
from app.models.usuario import Usuario
from app.services import archivo_service


def _es_lider(db: Session, id_usuario: int, id_grupo: int) -> bool:
    integrante = grupo_repository.obtener_integrante(db, id_usuario, id_grupo)
    return integrante is not None and integrante.rol == "lider"

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
    if tarea.id_grupo is not None and not _es_lider(db, id_usuario, tarea.id_grupo):
        es_asignado = asignacion_tarea_repository.usuario_tiene_asignacion(
            db, tarea.id_tarea, id_usuario
        )
        if not es_asignado or not cambios or set(cambios) - {"estado"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para modificar esta tarea.",
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
            estado_nuevo
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
        return tarea
    except Exception:
        db.rollback()
        raise

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

def listar_asignados_de_tarea(db: Session, id_tarea: int, id_usuario: int) -> List[Usuario]:
    # obtener_tarea ya valida el acceso: dueño en las individuales y miembro del grupo
    # en las grupales. Cualquier miembro del grupo puede ver los asignados (RF-045).
    tarea = obtener_tarea(db, id_tarea, id_usuario)
    return asignacion_tarea_repository.obtener_usuarios_asignados(db, tarea.id_tarea)

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
