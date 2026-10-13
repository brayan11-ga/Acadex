# usuario_service
import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
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
    nombre_usuario: str | None = None,
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
        nombre_perfil = nombre_usuario or correo_electronico.split("@")[0]
        perfil_repo.create_perfil(db, {
            "id_usuario": usuario.id_usuario,
            "nombre_usuario": nombre_perfil,
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

INTENTOS_FALLIDOS_ANTES_DE_BLOQUEO = 5
DURACION_BLOQUEO_SEGUNDOS = 15 * 60


def login(db: Session, correo_electronico: str, contrasena: str) -> str:
    usuario = repo.get_usuario_by_correo(db, correo_electronico)
    credenciales_incorrectas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Correo o contraseña incorrectos",
    )

    if not usuario:
        raise credenciales_incorrectas

    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    if usuario.bloqueado and usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
        espera = max(1, int((usuario.bloqueado_hasta - ahora).total_seconds()))
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Cuenta bloqueada temporalmente por demasiados intentos fallidos",
            headers={"Retry-After": str(espera)},
        )

    # Libera bloqueos vencidos y bloqueos permanentes de versiones antiguas.
    if usuario.bloqueado or usuario.bloqueado_hasta is not None:
        usuario.bloqueado = False
        usuario.bloqueado_hasta = None
        usuario.intentos_fallidos = 0

    if not verify_password(contrasena, usuario.contrasena):
        usuario.intentos_fallidos += 1
        bloqueada = usuario.intentos_fallidos >= INTENTOS_FALLIDOS_ANTES_DE_BLOQUEO
        if bloqueada:
            usuario.bloqueado = True
            usuario.bloqueado_hasta = ahora + timedelta(seconds=DURACION_BLOQUEO_SEGUNDOS)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        if bloqueada:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Cuenta bloqueada temporalmente por demasiados intentos fallidos",
                headers={"Retry-After": str(DURACION_BLOQUEO_SEGUNDOS)},
            )
        raise credenciales_incorrectas

    usuario.intentos_fallidos = 0
    usuario.bloqueado = False
    usuario.bloqueado_hasta = None
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

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

def _hash_token_reset(valor: str) -> str:
    digest = hashlib.sha256(valor.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def generar_token_reset_password(db: Session, id_usuario: int) -> tuple[TokenTemporal, str]:
    usuario = repo.get_usuario_by_id(db, id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        db.query(TokenTemporal).filter(
            TokenTemporal.id_usuario == id_usuario,
            TokenTemporal.tipo_token == "reset_password",
            TokenTemporal.usado.is_(False),
        ).update({"usado": True}, synchronize_session=False)

        valor_token = secrets.token_urlsafe(24)
        nuevo_token = TokenTemporal(
            tipo_token="reset_password",
            # Persist only a one-way digest. The raw secret is returned once to
            # the caller for delivery and is never stored in PostgreSQL.
            valor_token=_hash_token_reset(valor_token),
            fecha_expiracion=ahora + timedelta(minutes=15),
            usado=False,
            id_usuario=id_usuario,
            id_grupo=None,
        )
        db.add(nuevo_token)
        db.commit()
        db.refresh(nuevo_token)
    except Exception:
        db.rollback()
        raise

    return nuevo_token, valor_token


def solicitar_reset_por_correo(db: Session, correo: str) -> tuple[TokenTemporal, str] | None:
    usuario = repo.get_usuario_by_correo(db, correo)
    if not usuario:
        return None

    return generar_token_reset_password(db, usuario.id_usuario)


def invalidar_token_reset(db: Session, token: TokenTemporal) -> None:
    token.usado = True
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def restablecer_password_con_token(db: Session, token: str, nueva: str) -> None:
    invalido = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token inválido o expirado",
    )
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    token_temporal = db.query(TokenTemporal).filter(
        TokenTemporal.valor_token == _hash_token_reset(token),
        TokenTemporal.tipo_token == "reset_password",
        TokenTemporal.usado.is_(False),
        TokenTemporal.fecha_expiracion > ahora,
    ).first()
    if (
        not token_temporal
        or token_temporal.usado
        or token_temporal.id_usuario is None
        or token_temporal.fecha_expiracion <= ahora
    ):
        raise invalido

    usuario = repo.get_usuario_by_id(db, token_temporal.id_usuario)
    if not usuario:
        raise invalido

    try:
        # Claim the token with a conditional UPDATE so concurrent requests cannot
        # both use the same reset link.
        reclamado = db.query(TokenTemporal).filter(
            TokenTemporal.id_token == token_temporal.id_token,
            TokenTemporal.usado.is_(False),
            TokenTemporal.fecha_expiracion > ahora,
        ).update({"usado": True}, synchronize_session=False)
        if reclamado != 1:
            db.rollback()
            raise invalido

        usuario.contrasena = hash_password(nueva)
        usuario.intentos_fallidos = 0
        usuario.bloqueado = False
        usuario.bloqueado_hasta = None
        db.query(TokenTemporal).filter(
            TokenTemporal.id_usuario == usuario.id_usuario,
            TokenTemporal.tipo_token == "reset_password",
            TokenTemporal.usado.is_(False),
        ).update({"usado": True}, synchronize_session=False)
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
