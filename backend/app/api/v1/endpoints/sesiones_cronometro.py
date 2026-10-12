from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.sesion_cronometro import SesionCronometroOut
from app.services import sesion_cronometro_service as service

router = APIRouter(prefix="/sesiones-cronometro", tags=["sesiones_cronometro"])

@router.post("/iniciar", response_model=SesionCronometroOut, status_code=201)
def iniciar_sesion(
    id_usuario: int,
    id_tarea: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    if id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes iniciar una sesión a nombre de otro usuario.",
        )
    return service.iniciar_sesion(db, usuario_actual.id_usuario, id_tarea)

@router.patch("/{id_sesion}/finalizar", response_model=SesionCronometroOut)
def finalizar_sesion(
    id_sesion: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return service.finalizar_sesion(db, id_sesion, usuario_actual.id_usuario)

@router.get("/usuario/{id_usuario}", response_model=list[SesionCronometroOut])
def listar_sesiones(
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    return service.listar_sesiones_usuario(db, id_usuario, usuario_actual.id_usuario)
