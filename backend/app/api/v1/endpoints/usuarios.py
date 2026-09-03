from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioOut
from app.schemas.auth import LoginRequest, Token
from app.services import usuario_service as service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return service.registrar_usuario(db, usuario.correo_electronico, usuario.contrasena)

@router.post("/login", response_model=Token)
def login(credenciales: LoginRequest, db: Session = Depends(get_db)):
    token = service.login(db, credenciales.correo_electronico, credenciales.contrasena)
    return Token(access_token=token)

@router.get("/{id_usuario}", response_model=UsuarioOut)
def leer_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return service.obtener_usuario(db, id_usuario)

@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.listar_usuarios(db, skip, limit)