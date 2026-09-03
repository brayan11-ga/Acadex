from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.dependencies.db import get_db
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/usuarios/login")

CREDENCIALES_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    payload = decode_access_token(token)
    if payload is None:
        raise CREDENCIALES_INVALIDAS

    try:
        id_usuario = int(payload.sub)
    except ValueError:
        raise CREDENCIALES_INVALIDAS

    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if usuario is None:
        raise CREDENCIALES_INVALIDAS

    return usuario