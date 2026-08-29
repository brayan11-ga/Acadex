from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class sesionCronometro(BaseModel):
    fecha_inicio:datetime
    id_usuario:int
    id_tareas:int

class sesionCronometroUpdate(BaseModel):
    fecha_fin:Optional[datetime] =None
    duracion:Optional[float]=None

class sesionCronometroOut(BaseModel):
    id_sesion:int
    fecha_inicio:datetime
    fecha_fin:Optional[datetime]=None
    duracion:Optional[float]=None
    id_usuario:int
    id_tarea:int

    class config:
        from_attributes=True
