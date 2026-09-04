# app/schemas/panel_schema.py
from pydantic import BaseModel
from typing import List, Optional

class TareaPanelSchema(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str] = None
    estado: str
    fechaVencimiento: str 
    etiqueta: Optional[str] = None

class DiaProgresoSchema(BaseModel):
    dia: str
    cantidad: int
    actual: Optional[bool] = False

class ProgresoDiarioSchema(BaseModel):
    completadas: int
    total: int
    dias: List[DiaProgresoSchema]

class DatosPanelResponse(BaseModel):
    tareaPrioritaria: Optional[TareaPanelSchema] = None
    progreso: Optional[ProgresoDiarioSchema] = None
    proximasTareas: List[TareaPanelSchema] = []