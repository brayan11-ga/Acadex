# usuario_service
import secrets
from datetime import datetime, timedelta
from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import create_access_token
from app.models.usuario import Usuario
from app.models.token_temporal import TokenTemporal
from app.models.consentimiento_usuario import ConsentimientoUsuario
from app.core.legal import VERSION_POLITICA_DATOS, VERSION_AVISO_ALMACENAMIENTO
from app.repositories import usuario_repository as repo
from app.repositories import perfil_repository as perfil_repo
from app.schemas.usuario import UsuarioUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def registrar_usuario(
    db: Session,
    correo_electronico: str,
    contrasena: str,
    acepta_tratamiento_datos: bool,
    confirma_aviso_almacenamiento: bool,
) -> Usuario:
    if not acepta_tratamiento_datos or not confirma_aviso_almacenamiento:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Debes aceptar el tratamiento de datos y confirmar la lectura de los avisos.",
        )
    if repo.get_usuario_by_correo(db, correo_electronico):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    hashed = hash_password(contrasena)
    try:
        usuario = repo.create_usuario(db, correo_electronico, hashed, commit=False)
        nombre_por_defecto = correo_electronico.split("@")[0]
        perfil_repo.create_perfil(db, {
            "id_usuario": usuario.id_usuario,
            "nombre_usuario": nombre_por_defecto,
        }, commit=False)
        db.add_all([
            ConsentimientoUsuario(
                id_usuario=usuario.id_usuario,
                tipo_consentimiento="tratamiento_datos",
                version_politica=VERSION_POLITICA_DATOS,
            ),
            ConsentimientoUsuario(
                id_usuario=usuario.id_usuario,
                tipo_consentimiento="aviso_almacenamiento",
                version_politica=VERSION_AVISO_ALMACENAMIENTO,
            ),
        ])
        db.commit()
        db.refresh(usuario)
    except Exception:
        db.rollback()
        raise

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
        # Tiempo de expiracion del token
        fecha_expiracion=datetime.utcnow() + timedelta(minutes=15),
        usado=False,
        id_usuario=id_usuario,
        id_grupo=None,
    )

    db.add(nuevo_token)
    db.commit()
    db.refresh(nuevo_token)

    return nuevo_token

# invalida los tokens de reset que nunaca fueron usados
def solicitar_reset_por_correo(db:Session,correo:str)->TokenTemporal | None:
    Usuario=repo.get_usuario_by_correo(db,correo)
    if not Usuario:
        return None

    db.query(TokenTemporal).filter(
        TokenTemporal.id_usuario==Usuario.id_usuario,
        TokenTemporal.tipo_token=="reset_password",
        TokenTemporal.usado.id_(False),
    ).update({"usado":True})
    return generar_token_reset_password(db. usuario.id_usuario)

def restablecer_password_con_token(db:str,token:str,nueva:str)-> None:
    invalido=HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token invalido o expirado"
    )
    t=db.query(TokenTemporal).filter(
        TokenTemporal.valor_token==token,
        TokenTemporal.tipo_token=="reset_password",
        TokenTemporal.usado.is_(False),
    ).first()
    if not t or t.id_usuario is None or t.fecha_expiracion<datetime.utcnow():
        raise invalido
    Usuario=repo.get_usuario_by_id(db,t.usuario)
    if not Usuario:
        raise invalido
    Usuario.contrasena=hash_password(nueva)
    t.usadi=True
    db.commit