from app.schemas.usuario import UsuarioUpdate 
from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import create_access_token
from app.models.usuario import Usuario
from app.repositories import usuario_repository as repo
from app.repositories import perfil_repository as perfil_repo

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
    usuario = repo.create_usuario(db, correo_electronico, hashed)

    # Todo usuario nuevo nace con su perfil ya creado, para que
    # /perfiles/me nunca le devuelva 404 la primera vez que entra
    nombre_por_defecto = correo_electronico.split("@")[0]
    perfil_repo.create_perfil(db, {
        "id_usuario": usuario.id_usuario,
        "nombre_usuario": nombre_por_defecto,
    })

    return usuario

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

def actualizar_usuario(db: Session, id_usuario: int, datos: UsuarioUpdate) -> Usuario:
    usuario = repo.get_usuario_by_id(db, id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    datos_dict = datos.model_dump(exclude_unset=True)
    return repo.update_usuario(db, usuario, datos_dict)


def eliminar_usuario(db: Session, id_usuario: int) -> None:
    usuario = repo.get_usuario_by_id(db, id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    repo.delete_usuario(db, usuario)