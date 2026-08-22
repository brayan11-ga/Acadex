# app/schemas/tarea.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class TareaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_entrega: datetime
    dificultad_estimada: int
    tiempo_estimado: int
    prioridad: Optional[int] = None
    id_categoria: int


class TareaCreate(TareaBase):
    id_usuario: Optional[int] = None
    id_grupo: Optional[int] = None

    @model_validator(mode="after")
    def validar_owner(self):
        tiene_usuario = self.id_usuario is not None
        tiene_grupo = self.id_grupo is not None
        if tiene_usuario == tiene_grupo:
            raise ValueError(
                "La tarea debe pertenecer a un usuario O a un grupo, no a ambos ni a ninguno"
            )
        return self


class TareaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    estado: Optional[str] = None
    dificultad_estimada: Optional[int] = None
    tiempo_estimado: Optional[int] = None
    prioridad: Optional[int] = None
    id_categoria: Optional[int] = None


class TareaResponse(TareaBase):
    id_tarea: int
    estado: str
    tiempo_acumulado: float
    cronometro_activo: bool
    id_usuario: Optional[int] = None
    id_grupo: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)