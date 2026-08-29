from sqlalchemy.orm import Sesion
from app.models import SesionesCronometro

def get_sesion_by_id(db:Sesion,id_sesion:int):
    return db.query(SesionesCronometro).filter(SesionesCronometro.id_sesion==id_sesion).first()

def get_sesiones_by_usuario(db:Sesion,id_usuario:int):
    return db.query(SesionesCronometro).filter(SesionesCronometro.id_usuario==id_usuario).all()

def get_sesion_activa(db:Sesion,id_tarea:int):
    return db.query(SesionesCronometro).filter(
        SesionesCronometro.id_tarea==id_tarea,
        SesionesCronometro.fecha_fin.is_(None)
    ).first()

def create_sesion(db:Sesion,data:dict):
    sesion=SesionesCronometro(**data)
    db.add(sesion)
    db.commit()
    db.refresh(sesion)
    return sesion

def update_sesion(db:Sesion,sesion:SesionesCronometro,data:dict):
    for key, value in data.items():
        setattr(sesion,key,value)
    db.commit()
    db.refresh(sesion)
    return sesion
