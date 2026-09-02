from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.sesion_cronometro import SesionCronometro
from app.repositories import sesion_cronometro_repository as repo

def iniciar_sesion(db: Session, id_usuario: int, id_tarea: int) -> SesionCronometro:
    if repo.get_sesion_activa(db, id_tarea):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya hay una sesión activa para esta tarea",
        )
    data = {"fecha_inicio": datetime.utcnow(), "id_usuario": id_usuario, "id_tarea": id_tarea}
    return repo.create_sesion(db, data)

def finalizar_sesion(db: Session, id_sesion: int) -> SesionCronometro:
    sesion = repo.get_sesion_by_id(db, id_sesion)
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada",
        )
    if sesion.fecha_fin is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La sesión ya fue finalizada",
        )

    fecha_fin = datetime.utcnow()
    duracion = (fecha_fin - sesion.fecha_inicio).total_seconds()
    return repo.update_sesion(db, sesion, {"fecha_fin": fecha_fin, "duracion": duracion})

def listar_sesiones_usuario(db: Session, id_usuario: int) -> List[SesionCronometro]:
    return repo.get_sesiones_by_usuario(db, id_usuario)