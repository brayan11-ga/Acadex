# repositories/SesionCronometro
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.sesion_cronometro import SesionCronometro

def get_sesion_by_id(db: Session, id_sesion: int) -> Optional[SesionCronometro]:
    return db.query(SesionCronometro).filter(SesionCronometro.id_sesion == id_sesion).first()

def get_sesiones_by_usuario(db: Session, id_usuario: int) -> list[SesionCronometro]:
    return db.query(SesionCronometro).filter(SesionCronometro.id_usuario == id_usuario).all()

def get_sesion_activa(db: Session, id_tarea: int) -> Optional[SesionCronometro]:
    return db.query(SesionCronometro).filter(
        SesionCronometro.id_tarea == id_tarea,
        SesionCronometro.fecha_fin.is_(None)
    ).first()


def get_sesion_activa_de_usuario(
    db: Session, id_tarea: int, id_usuario: int
) -> Optional[SesionCronometro]:
    """Sesión abierta de ESE usuario en esa tarea (el cronómetro es personal)."""
    return db.query(SesionCronometro).filter(
        SesionCronometro.id_tarea == id_tarea,
        SesionCronometro.id_usuario == id_usuario,
        SesionCronometro.fecha_fin.is_(None),
    ).first()


def sumar_duracion_cerrada(db: Session, id_tarea: int, id_usuario: int) -> float:
    """Suma la duración (segundos) de las sesiones cerradas del usuario en la tarea."""
    total = (
        db.query(func.coalesce(func.sum(SesionCronometro.duracion), 0))
        .filter(
            SesionCronometro.id_tarea == id_tarea,
            SesionCronometro.id_usuario == id_usuario,
            SesionCronometro.fecha_fin.is_not(None),
        )
        .scalar()
    )
    return float(total or 0)

def create_sesion(db: Session, data: dict) -> SesionCronometro:
    sesion = SesionCronometro(**data)
    db.add(sesion)
    db.commit()
    db.refresh(sesion)
    return sesion

def update_sesion(db: Session, sesion: SesionCronometro, data: dict) -> SesionCronometro:
    for key, value in data.items():
        setattr(sesion, key, value)
    db.commit()
    db.refresh(sesion)
    return sesion

def delete_sesiones_by_tarea(db:Session, id_tarea:int) ->None:
    db.query(SesionCronometro).filter(
        SesionCronometro.id_tarea==id_tarea
    ).delete(synchronize_session=False)
    db.commit()