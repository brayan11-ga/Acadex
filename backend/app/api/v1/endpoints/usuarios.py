from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.schemas.usuario import UsuarioCreate,UsuarioOut
from app.services import usuario_servicie as service

router=APIRouter(prefix="/usuarios",tags=["usuarios"])

@router.get("/",response_model=UsuarioOut,status_code=201)
def crear_usuario(usuario:UsuarioCreate,db:Session=Depends(get_db)):
    return service.registrar_usuario(db,usuario.correo_electronico,usuario.contrasena)

@router.get("/{users_id}",response_model=UsuarioOut)
def leer_usuario(id_usuario:int,db:Session=Depends(get_db)):
    return service.obtener_usuario(id,id_usuario)

@router.get("/",response_model=list[UsuarioOut])
def listar_usuarios(skipt:int=0, limit:int=100, db:Session=Depends(get_db)):
    return service.listar_usuarios(db,skipt,limit)