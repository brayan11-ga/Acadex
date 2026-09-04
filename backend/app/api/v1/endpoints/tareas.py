# app/api/v1/endpoints/tareas.py
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.tarea import TareaCreate, TareaUpdate, TareaResponse
from app.services import tarea_service

router = APIRouter(prefix="/tareas", tags=["Tareas"])


@router.post("/", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(datos: TareaCreate, db: Session = Depends(get_db)):
    return tarea_service.crear_tarea(db, datos)


@router.get("/", response_model=List[TareaResponse])
def listar_tareas(db: Session = Depends(get_db)):
    return tarea_service.listar_tareas(db)


@router.get("/calendario", response_model=List[TareaResponse])
def listar_tareas_calendario(
    desde: date,
    hasta: date,
    id_usuario: Optional[int] = None,
    id_grupo: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return tarea_service.listar_tareas_calendario(db, desde, hasta, id_usuario, id_grupo)


@router.get("/{id_tarea}", response_model=TareaResponse)
def obtener_tarea(id_tarea: int, db: Session = Depends(get_db)):
    return tarea_service.obtener_tarea(db, id_tarea)


@router.put("/{id_tarea}", response_model=TareaResponse)
def actualizar_tarea(id_tarea: int, datos: TareaUpdate, db: Session = Depends(get_db)):
    return tarea_service.actualizar_tarea(db, id_tarea, datos)


@router.delete("/{id_tarea}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tarea(id_tarea: int, db: Session = Depends(get_db)):
    tarea_service.eliminar_tarea(db, id_tarea)