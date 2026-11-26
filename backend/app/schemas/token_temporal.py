from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TokenResetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    valor_token: str
    fecha_expiracion: datetime
    id_usuario: int
