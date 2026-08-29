from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.repositories import usuario_repository as repo

pwd_context=CryptContext(chemes=["bcrypt"],deprecated="auto")

def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain:str,hashed:str)-> bool:
    return pwd_context.verify(plain,hashed)

def registrar_usuario(db:Session,correo_electronico:str,contrasena:str):
    if repo.get_usuario_by_emil(db,correo_electronico):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="El correo ya esta registrado")
    hashed=hash_password(contrasena)
    return repo.create_usuario(db,correo_electronico,hashed)

def obtener_usuario(db:Session,id_usuario:int):
    usuario=repo.get_usuario_by_id(db,id_usuario)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Usuario no encontrado")
    return usuario 
def listar_usuarios(db,Session,skip:int=0, limit:int=100):
    return repo.get_usuario(db,skip,limit)