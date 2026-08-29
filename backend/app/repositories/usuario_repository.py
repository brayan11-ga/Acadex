from sqlalchemy import Session
from backend.app.models import Usuarios

def get_usuario_by_id(db:Session,id_usuario:int):
    return db.query(Usuarios).filter(Usuarios.id_usuario==id_usuario).first()

def get_usuario_by_emil(db:Session,correo:str):
    return db.query(Usuarios).filter(Usuarios.correo_electronico==id-correo).first()

def ger_usuarios(db:Session,skip:int=0,limit:int=100):
    return db.query(Usuarios).offset(skip).limit(limit).all()

def create_usuario(db:Session,correo_electronico:str,contrasena_hash:str):
    usuario=Usuarios(correo_electronico=correo_electronico,contrsena=contrasena_hash)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def delete_usuario(db:Session,usuario:Usuarios):
    db.delete(usuario)
    db.commit()
    