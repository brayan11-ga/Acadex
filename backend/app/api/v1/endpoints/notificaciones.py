# backend/app/api/v1/endpoints/notificaciones.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

# Rutas exactas de tu proyecto
from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.notificacion_schema import NotificacionResponse
from app.models.notificacion import Notificacion

router = APIRouter(
    prefix="/api/v1/notificaciones",
    tags=["Notificaciones"]
)

@router.get("/", response_model=List[NotificacionResponse])
def listar_notificaciones(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    # Consultamos las notificaciones filtradas por el usuario actual autenticado por token
    notificaciones = db.query(Notificacion).filter(
        Notificacion.id_usuario == usuario_actual.id_usuario
    ).all()
    
    return notificaciones