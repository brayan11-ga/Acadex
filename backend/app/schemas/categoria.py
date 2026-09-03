# app/schemas/categoria.py
from pydantic import BaseModel, ConfigDict


class CategoriaResponse(BaseModel):
    id_categoria: int
    nombre_categoria: str

    model_config = ConfigDict(from_attributes=True)