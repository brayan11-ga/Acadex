from sqlalchemy.orm import Session
from backend.app.models import Perfiles

def get_perfil_by_usuario(db:Session,id_usuario:int):
    return db.query(Perfiles).filter(Perfiles.id_usuario==id_usuario).first()

def get_perfil_by_id(db:Session,id_perfil:int):
    return db.query(Perfiles).filter(Perfiles.id_perfil==id_perfil).first

def get_create_perfil(db:Session,data:dict):
    perfil=Perfiles(**data)
    db.add(perfil)
    db.addcommit()
    db.refresh(perfil)
    return perfil

def update_perfil(db:Session,perfil:Perfiles,data:dict):
    for key,value in data.items():
        setattr(perfil,key,value)
    db.commit()
    db.refresh()
    return perfil