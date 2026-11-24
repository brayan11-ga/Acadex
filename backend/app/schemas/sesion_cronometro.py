from datetime import datetime
from typing import Literal,Optional
from pydantic import BaseModel, ConfigDict

class SesionCronometroCreate(BaseModel):
    id_usuario: int
    id_tarea: int

class SesionCronometroEstado(BaseModel):
    estado:Literal["activa","aviso","pausada_automaticamente","cerrada"]
    limite_segundos:int
    segundos_gracia_restantes:Optional[int]=None
    sesion: SesionCronometroOut

class SesionCronometroOut(BaseModel):
    id_sesion: int
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    duracion: Optional[float] = None
    id_usuario: int
    id_tarea: int

    model_config = ConfigDict(from_attributes=True)

class CronometroTareaOut(BaseModel):
    segundos_acumulados:int
    segundos_sesion_actual:int =0
    limite_segundos:int
    sesion:Optional[SesionCronometroOut]=None

