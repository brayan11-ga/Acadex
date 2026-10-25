from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator, Field
from typing import List

from app.config.settings import (
    MAX_ARCHIVOS_POR_TAREA,
    MAX_ARCHIVOS_POR_TAREA_DEFECTO,
)

class TareaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_entrega: datetime
    dificultad_estimada: int = Field(..., ge=1, le=5)
    tiempo_estimado: int = Field(..., gt=0)
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
    dificultad_estimada: Optional[int] = Field(default=None, ge=1, le=5)
    tiempo_estimado: Optional[int] = Field(default=None, gt=0)
    prioridad: Optional[int] = None
    id_categoria: Optional[int] = None
    max_archivos: Optional[int] = Field(default=None, ge=1)

class TareaResponse(TareaBase):
    id_tarea: int
    estado: str
    tiempo_acumulado: float
    cronometro_activo: bool
    id_usuario: Optional[int] = None
    id_grupo: Optional[int] = None
    max_archivos: int
    total_archivos: int = 0

    model_config = ConfigDict(from_attributes=True)

class TareaGrupalCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_entrega: datetime
    dificultad_estimada: int = Field(..., ge=1, le=5)
    tiempo_estimado: int = Field(..., gt=0)
    id_categoria: int
    ids_usuarios: List[int] = Field(default_factory=list)
    max_archivos: int = Field(
        default=MAX_ARCHIVOS_POR_TAREA_DEFECTO, ge=1, le=MAX_ARCHIVOS_POR_TAREA
    )

class CompletarTareaRequest(BaseModel):
    dificultad_real: int = Field(..., ge=1, le=5)

class ReasignarAsignadosRequest(BaseModel):
    # La lista es el conjunto completo nuevo; el service valida vacía/repetidos
    # para devolver 400 con el mensaje de negocio, no 422.
    ids_usuarios: List[int] = Field(default_factory=list)

class IntegranteAsignadoResponse(BaseModel):
    id_usuario: int
    correo_electronico: str
    completado: bool = False

    model_config = ConfigDict(from_attributes=True)