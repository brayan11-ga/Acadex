from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.perfil import Perfil
from app.repositories import perfil_repository as repo

def crear_perfil(db: Session, data: dict, id_usuario_actual: int) -> Perfil:
    if data.get("id_usuario") != id_usuario_actual:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear el perfil de otro usuario.",
        )
    datos_propios = {**data, "id_usuario": id_usuario_actual}
    if repo.get_perfil_by_usuario(db, id_usuario_actual):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este usuario ya tiene un perfil",
        )
    return repo.create_perfil(db, datos_propios)

def obtener_perfil_por_usuario(
    db: Session,
    id_usuario: int,
    id_usuario_actual: int,
    lanzar_error: bool = True,
):
    if id_usuario != id_usuario_actual:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este perfil.",
        )
    perfil = repo.get_perfil_by_usuario(db, id_usuario)
    if not perfil and lanzar_error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado",
        )
    return perfil

def actualizar_perfil(
    db: Session, id_usuario: int, data: dict, id_usuario_actual: int
) -> Perfil:
    perfil = obtener_perfil_por_usuario(db, id_usuario, id_usuario_actual)
    data_limpia = {k: v for k, v in data.items() if v is not None}
    return repo.update_perfil(db, perfil, data_limpia)
