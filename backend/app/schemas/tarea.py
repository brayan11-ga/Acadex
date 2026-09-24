# backend/app/schemas/tarea.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator, Field

class TareaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_entrega: datetime
    dificultad_estimada: int
    tiempo_estimado: int
    prioridad: Optional[int] = None
    id_categoria: int

class TareaPropuestaIA(BaseModel):
    titulo: str = Field(..., max_length=100)
    descripcion: Optional[str] = ""
    dificultad_estimada: int = Field(default=3, ge=1, le=5)
    tiempo_estimado: int = Field(default=60, gt=0)
    id_categoria: Optional[int] = None

    @model_validator(mode="after")
    def sanear_campos_ia(self):
        if not (1 <= self.dificultad_estimada <= 5):
            self.dificultad_estimada = 3
        if self.tiempo_estimado <= 0:
            self.tiempo_estimado = 60
        if len(self.titulo) > 100:
            self.titulo = self.titulo[:97] + "..."
        return self

class TareaCreate(TareaBase):
    id_usuario: Optional[int] = None
    id_grupo: Optional[int] = None

    @model_validator(mode="after")
    def validar_owner(self):
        if self.id_usuario is not None and self.id_grupo is not None:
            raise ValueError(
                "La tarea no puede pertenecer a un usuario y a un grupo al mismo tiempo"
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