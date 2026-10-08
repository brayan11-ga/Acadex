# backend/app/repositories/notificacion_repository.py
from typing import Optional
from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion


def crear_notificacion(
    db: Session, titulo: str, detalles: str, tipo: str, id_usuario: int, id_tarea: Optional[int] = None
) -> Notificacion:
    notificacion = Notificacion(
        titulo=titulo,
        detalles=detalles,
        tipo=tipo,
        id_usuario=id_usuario,
        id_tarea=id_tarea,
    )
    db.add(notificacion)
    db.commit()
    db.refresh(notificacion)
    return notificacion