from datetime import date, datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.tarea import Tarea
from app.models.historial_tarea import HistorialTarea
from app.repositories import tarea_repository
from app.schemas.tarea import TareaCreate, TareaUpdate
from app.repositories import asignacion_tarea_repository, grupo_repository
from app.schemas.tarea import TareaGrupalCreate
from app.repositories import asignacion_tarea_repository
from app.models.usuario import Usuario


def crear_tarea(db: Session, datos: TareaCreate) -> Tarea:
    return tarea_repository.crear_tarea(db, datos)

def obtener_tarea(db: Session, id_tarea: int) -> Tarea:
    tarea = tarea_repository.obtener_tarea_por_id(db, id_tarea)
    if tarea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la tarea con id {id_tarea}",
        )
    return tarea

def listar_tareas(db: Session) -> List[Tarea]:
    return tarea_repository.obtener_todas_las_tareas(db)

def actualizar_tarea(db: Session, id_tarea: int, datos: TareaUpdate) -> Tarea:
    tarea = obtener_tarea(db, id_tarea)
    estado_anterior = tarea.estado

    # Actualizamos la tarea mediante el repositorio
    tarea_actualizada = tarea_repository.actualizar_tarea(db, tarea, datos)
    estado_nuevo = tarea_actualizada.estado

    # Sincronización automática con la tabla HistorialTarea para el gráfico del panel
    if estado_nuevo and estado_anterior:
        # Si se completó y antes no lo estaba
        if estado_nuevo.lower() == "completada" and estado_anterior.lower() != "completada":
            historial_existente = db.query(HistorialTarea).filter(
                HistorialTarea.id_tarea == tarea_actualizada.id_tarea,
                HistorialTarea.id_usuario == tarea_actualizada.id_usuario
            ).first()

            if not historial_existente:
                nuevo_historial = HistorialTarea(
                    id_tarea=tarea_actualizada.id_tarea,
                    id_usuario=tarea_actualizada.id_usuario,
                    fechahora_fin=datetime.now(),
                    tiempo_real=tarea_actualizada.tiempo_acumulado,
                    dificultad_real=tarea_actualizada.dificultad_estimada,
                )
                db.add(nuevo_historial)
                db.commit()

                from app.services import estadistica_service
                estadistica_service.recalcular_estadistica_categoria(
                    db, tarea_actualizada.id_usuario, tarea_actualizada.id_categoria
                )

        # Si se reabrió (pasa de completada a pendiente/otro estado)
        elif estado_nuevo.lower() != "completada" and estado_anterior.lower() == "completada":
            db.query(HistorialTarea).filter(
                HistorialTarea.id_tarea == tarea_actualizada.id_tarea,
                HistorialTarea.id_usuario == tarea_actualizada.id_usuario
            ).delete()
            db.commit()

            from app.services import estadistica_service
            estadistica_service.recalcular_estadistica_categoria(
                db, tarea_actualizada.id_usuario, tarea_actualizada.id_categoria
            )

    return tarea_actualizada

def eliminar_tarea(db: Session, id_tarea: int) -> None:
    tarea = obtener_tarea(db, id_tarea)
    tarea_repository.eliminar_tarea(db, tarea)

def listar_tareas_calendario(
    db: Session,
    desde: date,
    hasta: date,
    id_usuario: Optional[int] = None,
    id_grupo: Optional[int] = None,
) -> List[Tarea]:
    return tarea_repository.obtener_tareas_por_rango(db, desde, hasta, id_usuario, id_grupo)

def crear_tarea_grupal(db: Session, id_grupo: int, datos: TareaGrupalCreate) -> Tarea:
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
    tarea = tarea_repository.crear_tarea(db, tarea_datos)

    for id_usuario in datos.ids_usuarios:
        integrante = grupo_repository.obtener_integrante(db, id_usuario, id_grupo)
        if not integrante:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El usuario {id_usuario} no pertenece a este grupo",
            )
        asignacion_tarea_repository.crear_asignacion(db, tarea.id_tarea, integrante.id_integrante)

    return tarea

def listar_tareas_asignadas(db: Session, id_usuario: int) -> List[Tarea]:
    return asignacion_tarea_repository.obtener_tareas_asignadas_a_usuario(db, id_usuario)

def listar_tareas_de_grupo(db: Session, id_grupo: int) -> List[Tarea]:
    return tarea_repository.obtener_tareas_por_grupo(db, id_grupo)

def listar_asignados_de_tarea(db: Session, id_tarea: int) -> List[Usuario]:
    tarea = obtener_tarea(db, id_tarea)  # reutiliza la validación de que la tarea exista (lanza 404 si no)
    return asignacion_tarea_repository.obtener_usuarios_asignados(db, tarea.id_tarea)