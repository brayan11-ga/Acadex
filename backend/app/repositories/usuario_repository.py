from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.usuario import Usuario

def get_usuario_by_id(db: Session, id_usuario: int) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

def get_usuario_by_correo(db: Session, correo: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.correo_electronico == correo).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()

def create_usuario(db: Session, correo_electronico: str, contrasena_hash: str) -> Usuario:
    usuario = Usuario(correo_electronico=correo_electronico, contrasena=contrasena_hash)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def delete_usuario(db: Session, usuario: Usuario) -> None:
    db.delete(usuario)
    db.commit()