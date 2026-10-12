# backend/app/repositories/archivo_repository.py
from typing import List
from sqlalchemy.orm import Session
from app.models.archivo import Archivo


def crear_archivo(
    db: Session,
    nombre: str,
    tamano: int,
    tipo: str,
    ruta: str,
    id_tarea: int,
    id_usuario_subida: int,
) -> Archivo:
    archivo = Archivo(
        nombre=nombre,
        tamano=tamano,
        tipo=tipo,
        ruta=ruta,
        id_tarea=id_tarea,
        id_usuario_subida=id_usuario_subida,
    )
    db.add(archivo)
    db.commit()
    db.refresh(archivo)
    return archivo


def obtener_archivos_de_tarea(db: Session, id_tarea: int) -> List[Archivo]:
    return db.query(Archivo).filter(Archivo.id_tarea == id_tarea).all()


def obtener_archivo_de_tarea(db: Session, id_tarea: int, id_archivo: int) -> Archivo | None:
    return (
        db.query(Archivo)
        .filter(Archivo.id_tarea == id_tarea, Archivo.id_archivo == id_archivo)
        .first()
    )


def existe_otra_referencia_a_ruta(db: Session, ruta: str, id_archivo: int | None = None) -> bool:
    consulta = db.query(Archivo.id_archivo).filter(Archivo.ruta == ruta)
    if id_archivo is not None:
        consulta = consulta.filter(Archivo.id_archivo != id_archivo)
    return consulta.first() is not None


def existe_referencia_fuera_de_tarea(db: Session, ruta: str, id_tarea: int) -> bool:
    return (
        db.query(Archivo.id_archivo)
        .filter(Archivo.ruta == ruta, Archivo.id_tarea != id_tarea)
        .first()
        is not None
    )


def eliminar_archivo(db: Session, archivo: Archivo) -> None:
    db.delete(archivo)
    db.commit()
