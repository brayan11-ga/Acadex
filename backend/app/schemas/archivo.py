# backend/app/schemas/archivo.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ArchivoResponse(BaseModel):
    id_archivo: int
    nombre: str
    tamano: Optional[int] = None
    tipo: str
    fecha_adjuncion: datetime
    id_tarea: int
    puede_eliminar: bool = False

    model_config = ConfigDict(from_attributes=True)
