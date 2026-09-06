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


# --- Rutas nuevas: las que va a usar el frontend del Perfil ---

@router.get("/me", response_model=PerfilOut)
def leer_mi_perfil(
    usuario_actual: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
):
    return service.obtener_perfil_por_usuario(db, usuario_actual.id_usuario)


@router.patch("/me", response_model=PerfilOut)
def actualizar_mi_perfil(
    cambios: PerfilUpdate,
    usuario_actual: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
):
    return service.actualizar_perfil(db, usuario_actual.id_usuario, cambios.model_dump())


# --- Rutas antiguas: se conservan por si algo más las está usando ---
# ⚠️ Pendiente a futuro: no validan que el usuario solo vea/edite su propio perfil.

@router.get("/usuario/{id_usuario}", response_model=PerfilOut)
def leer_perfil_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return service.obtener_perfil_por_usuario(db, id_usuario)


@router.patch("/usuario/{id_usuario}", response_model=PerfilOut)
def actualizar_perfil(id_usuario: int, cambios: PerfilUpdate, db: Session = Depends(get_db)):
    return service.actualizar_perfil(db, id_usuario, cambios.model_dump())