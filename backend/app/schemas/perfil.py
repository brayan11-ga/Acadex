from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class PerfilBase(BaseModel):
    nombre_usuario: str
    telefono: Optional[str] = None
    foto_perfil: Optional[str] = None
    descripcion: Optional[str] = None
    notif_activas: bool = True
    limite_cronometro: Optional[int] = None
    limite_cronometro:Optional[int]=Field(default=None, gt=0)

class PerfilCreate(PerfilBase):
    id_usuario: int

class PerfilUpdate(BaseModel):
    nombre_usuario: Optional[str] = None
    telefono: Optional[str] = None
    foto_perfil: Optional[str] = None
    descripcion: Optional[str] = None
    notif_activas: Optional[bool] = None
    limite_cronometro: Optional[int,] = None
    limite_cronometro:Optional[int]=Field(default=None, gt=0)

class PerfilOut(PerfilBase):
    id_perfil: int
    id_usuario: int

    model_config = ConfigDict(from_attributes=True)