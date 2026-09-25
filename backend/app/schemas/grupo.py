from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GrupoCreate(BaseModel):
    nombre_grupo: str = Field(..., max_length=50)
    descripcion: Optional[str] = None


class GrupoResponse(BaseModel):
    id_grupo: int
    nombre_grupo: str
    descripcion: Optional[str] = None
    codigo_acceso: str
    fecha_creacion: date

    model_config = ConfigDict(from_attributes=True)


class GrupoConRolResponse(GrupoResponse):
    rol: str


class GrupoJoinRequest(BaseModel):
    codigo_acceso: str = Field(..., max_length=20)


class IntegranteResponse(BaseModel):
    id_integrante: int
    id_usuario: int
    correo_electronico: str
    rol: str
    fecha_ingreso: date

    model_config = ConfigDict(from_attributes=True)