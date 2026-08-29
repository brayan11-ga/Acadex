from pydantic import BaseModel,EmailStr
from datetime import date

class UsuarioBase(BaseModel):
    correo_electronico:str

class UsuarioCreate(BaseModel):
    contrasena:str

class UsuarioOut(BaseModel):
    id_usuario:int
    fecha_registro:date
    es_admin:bool

    class config:
        from_attributes=True