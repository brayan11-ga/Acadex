from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import create_access_token
from app.models.usuario import Usuario
from app.repositories import usuario_repository as repo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def registrar_usuario(db: Session, correo_electronico: str, contrasena: str) -> Usuario:
    if repo.get_usuario_by_correo(db, correo_electronico):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    hashed = hash_password(contrasena)
    return repo.create_usuario(db, correo_electronico, hashed)

def login(db: Session, correo_electronico: str, contrasena: str) -> str:
    usuario = repo.get_usuario_by_correo(db, correo_electronico)
    credenciales_incorrectas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Correo o contraseña incorrectos",
    )

    if not usuario:
        raise credenciales_incorrectas
    if not verify_password(contrasena, usuario.contrasena):
        raise credenciales_incorrectas

    return create_access_token(subject=str(usuario.id_usuario))

def obtener_usuario(db: Session, id_usuario: int) -> Usuario:
    usuario = repo.get_usuario_by_id(db, id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return usuario

def listar_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    return repo.get_usuarios(db, skip, limit)