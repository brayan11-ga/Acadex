from typing import Optional
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