from typing import Optional
from sqlalchemy.orm import Session
from app.models.perfil import Perfil

def get_perfil_by_usuario(db: Session, id_usuario: int) -> Optional[Perfil]:
    return db.query(Perfil).filter(Perfil.id_usuario == id_usuario).first()

def get_perfil_by_id(db: Session, id_perfil: int) -> Optional[Perfil]:
    return db.query(Perfil).filter(Perfil.id_perfil == id_perfil).first()

def create_perfil(db: Session, data: dict) -> Perfil:
    perfil = Perfil(**data)
    db.add(perfil)
    db.commit()
    db.refresh(perfil)
    return perfil

def update_perfil(db: Session, perfil: Perfil, data: dict) -> Perfil:
    for key, value in data.items():
        setattr(perfil, key, value)
    db.commit()
    db.refresh(perfil)
    return perfil