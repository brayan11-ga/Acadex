# endpointsUsuario
import logging
from typing import List

from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual, requerir_admin
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.schemas.auth import LoginRequest, Token, ForgotPasswordIn, ResetPasswordIn
from app.schemas.token_temporal import TokenResetOut
from app.models.usuario import Usuario
from app.services import usuario_service as service
from app.services.email_service import enviar_reset
from app.config.settings import settings
from app.core.registration_guard import registrar_intento

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    usuario: UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    registrar_intento(request.client.host if request.client else "desconocido")
    if usuario.sitio_web.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo procesar el registro.")
    return service.registrar_usuario(
        db,
        usuario.correo_electronico,
        usuario.contrasena,
        usuario.acepta_tratamiento_datos,
        usuario.confirma_aviso_almacenamiento,
        nombre_usuario=usuario.nombre_usuario,
    )

@router.post("/login", response_model=Token)
def login(credenciales: LoginRequest, db: Session = Depends(get_db)):
    token = service.login(db, credenciales.correo_electronico, credenciales.contrasena)
    return Token(access_token=token)

@router.get("/me", response_model=UsuarioOut)
def leer_usuario_actual(usuario_actual: Usuario = Depends(get_usuario_actual)):
    return usuario_actual

@router.post("/{id_usuario}/restablecer-password", response_model=TokenResetOut)
def restablecer_password(
    id_usuario: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin),
):
    token, valor_token = service.generar_token_reset_password(db, id_usuario)
    return TokenResetOut(
        valor_token=valor_token,
        fecha_expiracion=token.fecha_expiracion,
        id_usuario=token.id_usuario,
    )

@router.put("/{id_usuario}", response_model=UsuarioOut)
def actualizar_usuario(
    id_usuario: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin),
):
    return service.actualizar_usuario(db, id_usuario, usuario)

@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(
    skip: int = 0,
    limit: int = 100, 
    db: Session = Depends(get_db),
    admin:Usuario=Depends(requerir_admin),
    ):
    return service.listar_usuarios(db, skip, limit)

@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin),
):
    service.eliminar_usuario(db, id_usuario)
    return None

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordIn,
    db: Session = Depends(get_db),
):
    if not settings.password_reset_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La recuperación de contraseña no está configurada.",
        )

    solicitud = service.solicitar_reset_por_correo(db, data.correo_electronico)
    if solicitud:
        token, valor_token = solicitud
        try:
            enviar_reset(data.correo_electronico, valor_token)
        except Exception:
            logging.getLogger(__name__).exception("No se pudo enviar el correo de recuperación")
            try:
                service.invalidar_token_reset(db, token)
            except Exception:
                logging.getLogger(__name__).exception("No se pudo invalidar el token no entregado")
    return {"mensaje": "Si el correo existe, recibirás un enlace"}

@router.post("/reset-password")
def reset_password(data: ResetPasswordIn, db: Session = Depends(get_db)):
    service.restablecer_password_con_token(db, data.token, data.nueva_contrasena)
    return {"mensaje": "Contraseña actualizada"}
