# Ruta: backend/app/repositories/historial_tarea_repository.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.historial_tarea import HistorialTarea


def obtener_fila(
    db: Session, id_usuario: int, id_tarea: int
) -> Optional[HistorialTarea]:
    """Devuelve la fila de historial de un usuario en una tarea (o None)."""
    return (
        db.query(HistorialTarea)
        .filter(
            HistorialTarea.id_usuario == id_usuario,
            HistorialTarea.id_tarea == id_tarea,
        )
        .order_by(HistorialTarea.id_historial)
        .first()
    )


def obtener_filas(db: Session, id_tarea: int) -> List[HistorialTarea]:
    """Devuelve todas las filas de historial de una tarea."""
    return (
        db.query(HistorialTarea)
        .filter(HistorialTarea.id_tarea == id_tarea)
        .order_by(HistorialTarea.id_historial)
        .all()
    )


def eliminar_por_tarea(db: Session, id_tarea: int) -> int:
    """Borra todo el historial de una tarea (C4b) y devuelve cuántas filas quitó.

    No hace commit: la reapertura y este borrado deben confirmarse juntos en
    una sola transacción desde el service.
    """
    filas = (
        db.query(HistorialTarea)
        .filter(HistorialTarea.id_tarea == id_tarea)
        .all()
    )
    for fila in filas:
        db.delete(fila)
    db.flush()
    return len(filas)


def obtener_usuarios_completados(db: Session, id_tarea: int) -> set[int]:
    """IDs de usuarios que ya tienen al menos una fila de historial en la tarea."""
    filas = (
        db.query(HistorialTarea.id_usuario)
        .filter(HistorialTarea.id_tarea == id_tarea)
        .distinct()
        .all()
    )
    return {id_usuario for (id_usuario,) in filas}


def usuario_ya_completo(db: Session, id_tarea: int, id_usuario: int) -> bool:
    """True si ese usuario ya registró su parte en la tarea."""
    return obtener_fila(db, id_usuario, id_tarea) is not None


def upsert(
    db: Session,
    id_tarea: int,
    id_usuario: int,
    id_grupo: Optional[int],
    dificultad_real: int,
    tiempo_real: float,
    commit: bool = False,
) -> HistorialTarea:
    """Crea o actualiza la fila de historial del usuario en la tarea.

    La tabla no tiene una restricción única (id_usuario, id_tarea), así que se
    deduplica a mano: sobrevive la fila más antigua y las demás se eliminan.
    """
    filas = (
        db.query(HistorialTarea)
        .filter(
            HistorialTarea.id_usuario == id_usuario,
            HistorialTarea.id_tarea == id_tarea,
        )
        .order_by(HistorialTarea.id_historial)
        .all()
    )

    if filas:
        fila = filas[0]
        fila.fechahora_fin = datetime.now()
        fila.tiempo_real = tiempo_real
        fila.dificultad_real = dificultad_real
        if id_grupo is not None:
            fila.id_grupo = id_grupo
        for duplicado in filas[1:]:
            db.delete(duplicado)
    else:
        fila = HistorialTarea(
            id_tarea=id_tarea,
            id_usuario=id_usuario,
            id_grupo=id_grupo,
            fechahora_fin=datetime.now(),
            tiempo_real=tiempo_real,
            dificultad_real=dificultad_real,
        )
        db.add(fila)

    db.flush()
    if commit:
        db.commit()
        db.refresh(fila)
    return fila
