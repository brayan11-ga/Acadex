# app/api/v1/endpoints/panel.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.panel_schema import DatosPanelResponse
from app.services.panel_service import panel_service
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user  # <-- Importamos la dependencia de autenticación
from app.models.usuario import Usuario

router = APIRouter()

@router.get("/panel", response_model=DatosPanelResponse)
def obtener_panel_principal(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)  # <-- Obtenemos el usuario autenticado por su token JWT
):
    """
    Obtiene todos los datos consolidados (tarea prioritaria, próximas tareas y progreso) 
    para renderizar el panel principal del estudiante autenticado.
    """
    # Usamos el ID real del usuario que ha iniciado sesión (en tu caso, el ID 2)
    datos_panel = panel_service.obtener_datos_panel(db, id_usuario=current_user.id_usuario)
    
    return datos_panel