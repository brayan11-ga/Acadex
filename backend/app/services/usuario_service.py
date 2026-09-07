import secrets
from datetime import datetime, timedelta
from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import create_access_token
from app.models.usuario import Usuario
from app.models.token_temporal import TokenTemporal
from app.repositories import usuario_repository as repo
from app.repositories import perfil_repository as perfil_repo
from app.schemas.usuario import UsuarioUpdate

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

def generar_token_reset_password(db: Session, id_usuario: int) -> TokenTemporal:
    usuario = repo.get_usuario_by_id(db, id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    valor = secrets.token_urlsafe(24)

    nuevo_token = TokenTemporal(
        tipo_token="reset_password",
        valor_token=valor,
        fecha_expiracion=datetime.utcnow() + timedelta(hours=1),
        usado=False,
        id_usuario=id_usuario,
        id_grupo=None,
    )

    db.add(nuevo_token)
    db.commit()
    db.refresh(nuevo_token)

    return nuevo_token