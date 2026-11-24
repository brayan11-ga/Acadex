# backend/app/repositories/archivo_repository.py
from typing import List
from sqlalchemy import func
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
    commit: bool = True,
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
    if commit:
        db.commit()
    else:
        db.flush()
    db.refresh(archivo)
    return archivo


def obtener_archivos_de_tarea(db: Session, id_tarea: int) -> List[Archivo]:
    return db.query(Archivo).filter(Archivo.id_tarea == id_tarea).all()


def obtener_archivos_de_usuarios_en_tarea(
    db: Session, id_tarea: int, ids_usuarios: List[int]
) -> List[Archivo]:
    """Archivos de la tarea subidos por los usuarios indicados (C4c).

    Los archivos con id_usuario_subida NULL (históricos sin autor) no entran
    en el filtro y, por tanto, no se tocan.
    """
    if not ids_usuarios:
        return []
    return (
        db.query(Archivo)
        .filter(
            Archivo.id_tarea == id_tarea,
            Archivo.id_usuario_subida.in_(ids_usuarios),
        )
        .all()
    )


def eliminar_archivos_de_usuarios_en_tarea(
    db: Session, id_tarea: int, ids_usuarios: List[int]
) -> int:
    """Borra las filas de archivo de esos usuarios en la tarea (sin commit)."""
    filas = obtener_archivos_de_usuarios_en_tarea(db, id_tarea, ids_usuarios)
    for fila in filas:
        db.delete(fila)
    db.flush()
    return len(filas)


def contar_archivos_de_tarea(db: Session, id_tarea: int) -> int:
    """Cuenta los archivos de una sola tarea (validaciones puntuales)."""
    return (
        db.query(func.count(Archivo.id_archivo))
        .filter(Archivo.id_tarea == id_tarea)
        .scalar()
        or 0
    )


def obtener_conteo_archivos_por_tareas(
    db: Session, ids_tareas: List[int]
) -> dict[int, int]:
    """Cuenta los archivos de varias tareas en una sola consulta agrupada.

    Evita el problema N+1 al listar tareas: una sola consulta devuelve el
    conteo por tarea en lugar de una consulta por cada tarea.
    """
    if not ids_tareas:
        return {}
    filas = (
        db.query(Archivo.id_tarea, func.count(Archivo.id_archivo))
        .filter(Archivo.id_tarea.in_(ids_tareas))
        .group_by(Archivo.id_tarea)
        .all()
    )
    return {id_tarea: total for id_tarea, total in filas}


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
