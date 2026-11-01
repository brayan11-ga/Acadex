from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional;
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.sesion_cronometro import (SesionCronometroOut,SesionCronometroEstado, CronometroTareaOut)
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

@router.patch("/{id_sesion}/pausar", response_model=SesionCronometroOut)
def pausar_sesion(
    id_sesion:int,
    db:Session=Depends(get_db),
    usuario_actual:Usuario=Depends(get_usuario_actual),
):
    return service.pausar_sesion(db, id_sesion, usuario_actual.id_usuario)

@router.post("/tarea/{id_tarea}/iniciar", response_model=SesionCronometroOut,status_code=201)
def iniciar_por_tarea(
    id_tarea:int,
    db:Session=Depends(get_db),
    usuario_actual:Usuario=Depends(get_usuario_actual),
):
    return service.iniciar_sesion(db,usuario_actual.id_usuario,id_tarea)

@router.post("/tarea/{id_tarea}/reiniciar", response_model=CronometroTareaOut)
def reiniciar_tarea(
    id_tarea:int,
    db:Session=Depends(get_db),
    usuario_actual:Usuario=Depends(get_usuario_actual),
):
    service.reiniciar_tarea(db,id_tarea, usuario_actual.id_usuario)
    return service.obtener_estado_tarea(db, id_tarea, usuario_actual.id_usuario)

@router.get("/tarea/{id_tarea}/estado", response_model=CronometroTareaOut)
def estado_cronometro(
    id_tarea:int,
    db:Session=Depends(get_db),
    usuario_actual:Usuario=Depends(get_usuario_actual),
):
    return service.obtener_estado_tarea(db, id_tarea, usuario_actual.id_usuario)

@router.post("/{id_sesion}/verificar", response_model=SesionCronometroEstado)
def verificar_limite(
    id_sesion:int,
    db:Session=Depends(get_db),
    usuario_actual:Usuario=Depends(get_usuario_actual),
):
    return service.verificar_limite(db,id_sesion, usuario_actual.id_usuario)

@router.post("/{id_sesion}/confirmar", response_model=SesionCronometroEstado)
def confirmar_continuar(
    id_sesion:int,
    db:Session=Depends(get_db),
    usuario_actual:Usuario=Depends(get_usuario_actual)
):
    return service.confirmar_continuar(db, id_sesion, usuario_actual.id_usuario)
