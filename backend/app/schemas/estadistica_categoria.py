from pydantic import BaseModel
from typing import Optional

class EstadisticaCategoriaOut(BaseModel):
    nombre_categoria: str
    promedio_tiempo: Optional[float] = None
    promedio_dificultad: Optional[float] = None
    total_tareas: Optional[int] = None

    class Config:
        from_attributes = True