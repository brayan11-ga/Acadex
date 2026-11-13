# backend/app/schemas/notificacion_schema.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificacionResponse(BaseModel):
    id_notificacion: int
    titulo: str
    detalles: Optional[str] = None
    fecha_envio: datetime
    estado: bool
    tipo: str

    class Config:
        from_attributes = True