from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.perfil import Perfil
from app.repositories import perfil_repository as repo

def crear_perfil(db: Session, data: dict) -> Perfil:
    if repo.get_perfil_by_usuario(db, data["id_usuario"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este usuario ya tiene un perfil",
        )
    return repo.create_perfil(db, data)

def obtener_perfil_por_usuario(db: Session, id_usuario: int) -> Perfil:
    perfil = repo.get_perfil_by_usuario(db, id_usuario)
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado",
        )
    return perfil

def actualizar_perfil(db: Session, id_usuario: int, data: dict) -> Perfil:
    perfil = obtener_perfil_por_usuario(db, id_usuario)
    data_limpia = {k: v for k, v in data.items() if v is not None}
    return repo.update_perfil(db, perfil, data_limpia)