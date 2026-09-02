from datetime import date
from pydantic import BaseModel, EmailStr, ConfigDict

class UsuarioBase(BaseModel):
    correo_electronico: EmailStr

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioOut(UsuarioBase):
    id_usuario: int
    fecha_registro: date
    es_admin: bool
    model_config = ConfigDict(from_attributes=True)