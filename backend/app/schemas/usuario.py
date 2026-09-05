from datetime import date
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UsuarioBase(BaseModel):
    correo_electronico: EmailStr

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioUpdate(BaseModel):
    correo_electronico:Optional[EmailStr]=None
    contrasena:Optional[str]=None

class UsuarioOut(UsuarioBase):
    id_usuario: int
    fecha_registro: date
    es_admin: bool
    model_config = ConfigDict(from_attributes=True)