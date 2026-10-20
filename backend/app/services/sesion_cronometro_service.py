from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.sesion_cronometro import SesionCronometro
from app.repositories import sesion_cronometro_repository as repo, tarea_repository
from app.services import tarea_service

def iniciar_sesion(db: Session, id_usuario: int, id_tarea: int) -> SesionCronometro:
    tarea=tarea_service.verificar_permiso_tarea(db, id_tarea, id_usuario, "cronometro")
    if repo.get_sesion_activa(db, id_tarea):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya hay una sesión activa para esta tarea",
        )
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    data = {"fecha_inicio": ahora, "id_usuario": id_usuario, "id_tarea": id_tarea}
    tarea.cronometro_activo=True
    try:
        return repo.create_sesion(db, data)
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya hay una sesión activa para esta tarea",
        ) from None

def listar_sesiones_usuario(
    db: Session, id_usuario: int, id_usuario_actual: int) -> List[SesionCronometro]:
    if id_usuario != id_usuario_actual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron sesiones",
        )
    return repo.get_sesiones_by_usuario(db, id_usuario)


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
    tarea=tarea_repository.obtener_tarea_por_id(db,sesion.id_tarea)
    if tarea is not None:
        tarea.tiempo_acumulado=(tarea.tiempo_acumulado or 0) + duracion /60 #tiempo acumulado se guarda en min
        tarea.cronometro_activo=False
        tarea.ultima_pausa=fecha_fin
    return repo.update_sesion(db, sesion, {"fecha_fin": fecha_fin, "duracion": duracion})
