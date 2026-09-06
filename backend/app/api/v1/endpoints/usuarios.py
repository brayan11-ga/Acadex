from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual, requerir_admin
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.schemas.auth import LoginRequest, Token
from app.models.usuario import Usuario
from app.services import usuario_service as service
from app.schemas.token_temporal import TokenResetOut
from app.dependencies.auth import requerir_admin

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return service.registrar_usuario(db, usuario.correo_electronico, usuario.contrasena)

@router.post("/login", response_model=Token)
def login(credenciales: LoginRequest, db: Session = Depends(get_db)):
    token = service.login(db, credenciales.correo_electronico, credenciales.contrasena)
    return Token(access_token=token)

@router.get("/me",response_model=UsuarioOut)
def leer_usuario_actual(usuario_actual:Usuario=Depends(get_usuario_actual)):
# devuelve los datos Usuario dueño del token
    return usuario_actual

@router.post("/{id_usuario}/restablecer-password", response_model=TokenResetOut)
def restablecer_password(
    id_usuario: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin),  # solo un admin puede generar el reset
):
    return service.generar_token_reset_password(db, id_usuario)

@router.put("/{id_usuario}", response_model=UsuarioOut)
def actualizar_usuario(
    id_usuario: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin), # solo verifica que sea admin, no se usa como db
):
    return service.actualizar_usuario(db, id_usuario, usuario)

@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.listar_usuarios(db, skip, limit)

@router.put("/{id_usuario}",response_model=UsuarioOut)
def actualizar_usuario(id_usuario:int,usuario:UsuarioUpdate,db:Session=Depends(requerir_admin),):
    return service.actualizar_usuario(db,id_usuario,usuario)

@router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_admin),
):
    service.eliminar_usuario(db, id_usuario)
    return None