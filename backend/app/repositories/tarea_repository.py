# app/repositories/tarea_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.tarea import Tarea
from app.schemas.tarea import TareaCreate, TareaUpdate

def crear_tarea(db: Session, datos: TareaCreate) -> Tarea:
    nueva_tarea = Tarea(**datos.model_dump())
    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)
    return nueva_tarea

def obtener_tarea_por_id(db: Session, id_tarea: int) -> Optional[Tarea]:
    return db.query(Tarea).filter(Tarea.id_tarea == id_tarea).first()

def obtener_todas_las_tareas(db: Session) -> List[Tarea]:
    return db.query(Tarea).all()

def actualizar_tarea(db: Session, tarea: Tarea, datos: TareaUpdate) -> Tarea:
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(tarea, campo, valor)
    db.commit()
    db.refresh(tarea)
    return tarea

def eliminar_tarea(db: Session, tarea: Tarea) -> None:
    db.delete(tarea)
    db.commit()