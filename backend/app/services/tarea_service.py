from datetime import date
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.tarea import Tarea
from app.repositories import tarea_repository
from app.schemas.tarea import TareaCreate, TareaUpdate

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
    return tarea_repository.actualizar_tarea(db, tarea, datos)

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