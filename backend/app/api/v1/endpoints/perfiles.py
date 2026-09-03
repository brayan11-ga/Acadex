from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.schemas.perfil import PerfilCreate, PerfilUpdate, PerfilOut
from app.services import perfil_service as service

router = APIRouter(prefix="/perfiles", tags=["perfiles"])

@router.post("/", response_model=PerfilOut, status_code=201)
def crear_perfil(perfil: PerfilCreate, db: Session = Depends(get_db)):
    return service.crear_perfil(db, perfil.model_dump())

@router.get("/usuario/{id_usuario}", response_model=PerfilOut)
def leer_perfil_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return service.obtener_perfil_por_usuario(db, id_usuario)

@router.patch("/usuario/{id_usuario}", response_model=PerfilOut)
def actualizar_perfil(id_usuario: int, cambios: PerfilUpdate, db: Session = Depends(get_db)):
    return service.actualizar_perfil(db, id_usuario, cambios.model_dump())