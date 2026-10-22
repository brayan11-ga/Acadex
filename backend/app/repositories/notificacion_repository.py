# backend/app/repositories/notificacion_repository.py
from typing import Optional
from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion


def crear_notificacion(
    db: Session,
    titulo: str,
    detalles: str,
    tipo: str,
    id_usuario: int,
    id_tarea: Optional[int] = None,
    *,
    commit: bool = True,
) -> Notificacion:
    notificacion = Notificacion(
        titulo=titulo,
        detalles=detalles,
        tipo=tipo,
        id_usuario=id_usuario,
        id_tarea=id_tarea,
    )
    db.add(notificacion)
    if commit:
        db.commit()
        db.refresh(notificacion)
    else:
        # C4b/C4c: permite crear la notificación dentro de la transacción
        # principal sin confirmarla por separado.
        db.flush()
    return notificacion