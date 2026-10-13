# app/repositories/tarea_repository.py
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.models.tarea import Tarea
from app.models.integrante import Integrante
from app.schemas.tarea import TareaCreate, TareaUpdate

def crear_tarea(db: Session, datos: TareaCreate, commit: bool = True) -> Tarea:
    nueva_tarea = Tarea(**datos.model_dump())
    db.add(nueva_tarea)
    db.flush()
    if commit:
        db.commit()
        db.refresh(nueva_tarea)
    return nueva_tarea

def obtener_tarea_por_id(db: Session, id_tarea: int) -> Optional[Tarea]:
    return db.query(Tarea).filter(Tarea.id_tarea == id_tarea).first()

def obtener_todas_las_tareas(db: Session) -> List[Tarea]:
    return db.query(Tarea).all()

def obtener_tareas_visibles_para_usuario(db: Session, id_usuario: int) -> List[Tarea]:
    grupos_usuario = select(Integrante.id_grupo).where(Integrante.id_usuario == id_usuario)
    return (
        db.query(Tarea)
        .filter(or_(Tarea.id_usuario == id_usuario, Tarea.id_grupo.in_(grupos_usuario)))
        .all()
    )

def actualizar_tarea(
    db: Session, tarea: Tarea, datos: TareaUpdate, commit: bool = True
) -> Tarea:
    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(tarea, campo, valor)
    db.flush()
    if commit:
        db.commit()
        db.refresh(tarea)
    return tarea

def eliminar_tarea(db: Session, tarea: Tarea) -> None:
    db.delete(tarea)
    db.commit()

def obtener_tareas_por_rango(
    db: Session,
    fecha_inicio: date,
    fecha_fin: date,
    id_usuario: int,
    id_grupo: Optional[int] = None,
) -> List[Tarea]:
    query = db.query(Tarea).filter(
        Tarea.fecha_entrega >= fecha_inicio,
        Tarea.fecha_entrega < fecha_fin + timedelta(days=1),
    )
    if id_grupo is not None:
        query = query.filter(Tarea.id_grupo == id_grupo)
    else:
        grupos_usuario = select(Integrante.id_grupo).where(Integrante.id_usuario == id_usuario)
        query = query.filter(
            or_(Tarea.id_usuario == id_usuario, Tarea.id_grupo.in_(grupos_usuario))
        )
    return query.order_by(Tarea.fecha_entrega).all()

def obtener_tareas_por_grupo(db: Session, id_grupo: int) -> List[Tarea]:
    return db.query(Tarea).filter(Tarea.id_grupo == id_grupo).all()
