# backend/app/api/v1/endpoints/perfiles.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.perfil import PerfilCreate, PerfilUpdate, PerfilOut
from app.services import perfil_service as service
from app.dependencies.auth import get_current_user
from app.models.usuario import Usuario

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

@router.get("/me", response_model=PerfilOut)
def leer_mi_perfil(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene el perfil del usuario autenticado actualmente."""
    perfil = service.obtener_perfil_por_usuario(db, current_user.id_usuario)
    if not perfil:
        # Si por alguna razón no tiene perfil creado aún, devolvemos un objeto básico con su correo
        return {
            "nombre_usuario": current_user.correo_electronico.split("@")[0],
            "telefono": "",
            "descripcion": "Estudiante en Acadex",
            "notif_activas": True,
            "limite_cronometro": 30,
            "id_usuario": current_user.id_usuario
        }
    return perfil