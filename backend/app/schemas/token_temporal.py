from pydantic import BaseModel
from datetime import datetime

class TokenResetOut(BaseModel):
    valor_token: str
    fecha_expiracion: datetime
    id_usuario: int

    class Config:
        from_attributes = True