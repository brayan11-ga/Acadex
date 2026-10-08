# backend/app/repositories/archivo_repository.py
from typing import List
from sqlalchemy.orm import Session
from app.models.archivo import Archivo


def crear_archivo(db: Session, nombre: str, tamano: int, tipo: str, ruta: str, id_tarea: int) -> Archivo:
    archivo = Archivo(nombre=nombre, tamano=tamano, tipo=tipo, ruta=ruta, id_tarea=id_tarea)
    db.add(archivo)
    db.commit()
    db.refresh(archivo)
    return archivo


def obtener_archivos_de_tarea(db: Session, id_tarea: int) -> List[Archivo]:
    return db.query(Archivo).filter(Archivo.id_tarea == id_tarea).all()