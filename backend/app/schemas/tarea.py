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
    titulo: str
    descripcion: str
    dificultad_estimada: int # Debe validarse entre 1 y 5
    tiempo_estimado: int # En minutos
    id_categoria: Optional[int] = None

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
    
# backend/app/schemas/tarea.py (Añadir al final)

class TareaPropuestaIA(BaseModel):
    titulo: str
    descripcion: str
    dificultad_estimada: int
    tiempo_estimado: int
    id_categoria: Optional[int] = None

    @model_validator(mode="after")
    def validar_restricciones_ia(self):
        if not (1 <= self.dificultad_estimada <= 5):
            self.dificultad_estimada = 3 # Valor por defecto seguro
        if self.tiempo_estimado <= 0:
            self.tiempo_estimado = 60 # 1 hora por defecto si la IA falla
        return self# backend/app/schemas/tarea.py (Añadir al final)

class TareaPropuestaIA(BaseModel):
    titulo: str
    descripcion: str
    dificultad_estimada: int
    tiempo_estimado: int
    id_categoria: Optional[int] = None

    @model_validator(mode="after")
    def validar_restricciones_ia(self):
        if not (1 <= self.dificultad_estimada <= 5):
            self.dificultad_estimada = 3 # Valor por defecto seguro
        if self.tiempo_estimado <= 0:
            self.tiempo_estimado = 60 # 1 hora por defecto si la IA falla
        return self