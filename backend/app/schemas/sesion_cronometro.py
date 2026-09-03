from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SesionCronometroCreate(BaseModel):
    id_usuario: int
    id_tarea: int

class SesionCronometroOut(BaseModel):
    id_sesion: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    duracion: Optional[float] = None
    id_usuario: int
    id_tarea: int

    model_config = ConfigDict(from_attributes=True)