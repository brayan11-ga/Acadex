from datetime import date
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Optional

class UsuarioBase(BaseModel):
    correo_electronico: EmailStr

class UsuarioCreate(UsuarioBase):
    nombre_usuario: str | None = Field(default=None, min_length=1, max_length=50)
    contrasena: str
    acepta_tratamiento_datos: bool
    confirma_aviso_almacenamiento: bool
    sitio_web: str = ""

    @field_validator("nombre_usuario")
    @classmethod
    def validar_nombre_usuario(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        nombre = valor.strip()
        if not nombre:
            raise ValueError("El nombre de usuario no puede estar vacío.")
        return nombre

class UsuarioUpdate(BaseModel):
    correo_electronico:Optional[EmailStr]=None
    contrasena:Optional[str]=None

class UsuarioOut(UsuarioBase):
    id_usuario: int
    fecha_registro: date
    es_admin: bool
    model_config = ConfigDict(from_attributes=True)
