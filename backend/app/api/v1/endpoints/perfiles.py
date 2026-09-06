# backend/app/api/v1/endpoints/perfiles.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.perfil import PerfilCreate, PerfilUpdate, PerfilOut
from app.services import perfil_service as service

router = APIRouter(prefix="/perfiles", tags=["perfiles"])

@router.post("/", response_model=PerfilOut, status_code=201)
def crear_perfil(perfil: PerfilCreate, db: Session = Depends(get_db)):
    return service.crear_perfil(db, perfil.model_dump())

# --- Rutas nuevas: integrando tu lógica de respaldo y la estructura de tu compañero ---

@router.get("/me", response_model=PerfilOut)
def leer_mi_perfil(
    usuario_actual: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
):
    # Usamos lanzar_error=False para que no explote si no existe el perfil en la BD
    perfil = service.obtener_perfil_por_usuario(db, usuario_actual.id_usuario, lanzar_error=False)
    
    if not perfil:
        # Objeto de respaldo seguro para que Pydantic no dé error de validación
        return {
            "id_perfil": 0,
            "nombre_usuario": usuario_actual.correo_electronico.split("@")[0],
            "telefono": "",
            "descripcion": "Estudiante en Acadex",
            "notif_activas": True,
            "limite_cronometro": 30,
            "id_usuario": usuario_actual.id_usuario
        }
    return perfil

@router.patch("/me", response_model=PerfilOut)
def actualizar_mi_perfil(
    cambios: PerfilUpdate,
    usuario_actual: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
):
    return service.actualizar_perfil(db, usuario_actual.id_usuario, cambios.model_dump())

# --- Rutas antiguas: se conservan tal cual las dejó tu equipo ---

@router.get("/usuario/{id_usuario}", response_model=PerfilOut)
def leer_perfil_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return service.obtener_perfil_por_usuario(db, id_usuario)

@router.patch("/usuario/{id_usuario}", response_model=PerfilOut)
def actualizar_perfil(id_usuario: int, cambios: PerfilUpdate, db: Session = Depends(get_db)):
    return service.actualizar_perfil(db, id_usuario, cambios.model_dump())