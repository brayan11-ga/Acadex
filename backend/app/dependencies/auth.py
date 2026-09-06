from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.core.security import decode_access_token
from app.models.usuario import Usuario
from app.repositories import usuario_repository as repo
from app.models.integrante import Integrante  # ajusta la ruta según cómo se llame tu archivo del modelo
security_scheme = HTTPBearer()

CREDENCIALES_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Usuario:

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise CREDENCIALES_INVALIDAS

    try:
        id_usuario = int(payload.sub)
    except (TypeError, ValueError):
        raise CREDENCIALES_INVALIDAS

    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()  # ✅ agregado .first()
    if not usuario:
        raise CREDENCIALES_INVALIDAS

    return usuario

def requerir_admin(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    if not usuario.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador"
        )
    return usuario 

# dependencies/auth.py (o permisos.py)

def requerir_lider_de_grupo(
    id_grupo: int,
    usuario: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
) -> Usuario:
    """
    Permite pasar si el usuario es admin de la app,
    O si es 'lider' específicamente de ESE grupo (id_grupo).
    """
    if usuario.es_admin:
        return usuario

    integrante = (
        db.query(Integrante)
        .filter(
            Integrante.id_usuario == usuario.id_usuario,
            Integrante.id_grupo == id_grupo,
            Integrante.rol == "lider",
        )
        .first()
    )

    if not integrante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de líder sobre este grupo",
        )

    return usuario