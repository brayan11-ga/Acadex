# backend/app/repositories/asignacion_tarea_repository.py
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.asignacion_tarea import AsignacionTarea
from app.models.integrante import Integrante
from app.models.tarea import Tarea
from app.models.usuario import Usuario

def crear_asignacion(db: Session, id_tarea: int, id_integrante: int) -> AsignacionTarea:
    asignacion = AsignacionTarea(id_tarea=id_tarea, id_integrante=id_integrante)
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    return asignacion


def obtener_asignaciones_de_tarea(db: Session, id_tarea: int) -> List[AsignacionTarea]:
    return db.query(AsignacionTarea).filter(AsignacionTarea.id_tarea == id_tarea).all()


def obtener_tareas_asignadas_a_usuario(db: Session, id_usuario: int) -> List[Tarea]:
    return (
        db.query(Tarea)
        .join(AsignacionTarea, AsignacionTarea.id_tarea == Tarea.id_tarea)
        .join(Integrante, Integrante.id_integrante == AsignacionTarea.id_integrante)
        .filter(Integrante.id_usuario == id_usuario)
        .all()
    )

def usuario_tiene_asignacion(db: Session, id_tarea: int, id_usuario: int) -> bool:
    return (
        db.query(AsignacionTarea)
        .join(Integrante, Integrante.id_integrante == AsignacionTarea.id_integrante)
        .filter(AsignacionTarea.id_tarea == id_tarea, Integrante.id_usuario == id_usuario)
        .first()
        is not None
    )

def obtener_usuarios_asignados(db: Session, id_tarea: int) -> List[Usuario]:
    return (
        db.query(Usuario)
        .join(Integrante, Integrante.id_usuario == Usuario.id_usuario)
        .join(AsignacionTarea, AsignacionTarea.id_integrante == Integrante.id_integrante)
        .filter(AsignacionTarea.id_tarea == id_tarea)
        .all()
    )