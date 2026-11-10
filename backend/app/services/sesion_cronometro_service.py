from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.sesion_cronometro import SesionCronometro
from app.repositories import sesion_cronometro_repository as repo
from app.services import tarea_service

def iniciar_sesion(db: Session, id_usuario: int, id_tarea: int) -> SesionCronometro:
    tarea_service.verificar_permiso_tarea(db, id_tarea, id_usuario, "cronometro")
    if repo.get_sesion_activa_de_usuario(db, id_tarea, id_usuario):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes una sesión activa en esta tarea",
        )
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    data = {"fecha_inicio": ahora, "id_usuario": id_usuario, "id_tarea": id_tarea}
    try:
        return repo.create_sesion(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya tienes una sesión activa en esta tarea",
        ) from None

def finalizar_sesion(db: Session, id_sesion: int, id_usuario: int) -> SesionCronometro:
    sesion = repo.get_sesion_by_id(db, id_sesion)
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada",
        )
    if sesion.id_usuario != id_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada",
        )
    if sesion.fecha_fin is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La sesión ya fue finalizada",
        )

    fecha_fin = datetime.now(timezone.utc).replace(tzinfo=None)
    duracion = (fecha_fin - sesion.fecha_inicio).total_seconds()
    return repo.update_sesion(db, sesion, {"fecha_fin": fecha_fin, "duracion": duracion})


def descartar_sesion(db: Session, id_sesion: int, id_usuario: int) -> None:
    """Borra una sesión abierta sin guardar su duración.

    Solo el dueño puede descartarla y solo si sigue en curso. Así se corrige
    el caso de un cronómetro que quedó corriendo por olvido.
    """
    sesion = repo.get_sesion_by_id(db, id_sesion)
    if not sesion or sesion.id_usuario != id_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada",
        )
    if sesion.fecha_fin is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La sesión ya fue finalizada",
        )
    repo.delete_sesion(db, sesion)


def listar_sesiones_usuario(
    db: Session, id_usuario: int, id_usuario_actual: int
) -> List[SesionCronometro]:
    if id_usuario != id_usuario_actual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron sesiones",
        )
    return repo.get_sesiones_by_usuario(db, id_usuario)
