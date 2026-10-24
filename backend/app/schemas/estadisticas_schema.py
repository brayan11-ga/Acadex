# app/schemas/estadisticas_schema.py
from pydantic import BaseModel
from typing import List, Optional, Literal

# 1. Bloque: Meta Semanal (Weekly Goal)
class MetaSemanalSchema(BaseModel):
    porcentaje: int        # Ej: 82
    completadas: int       # Ej: 41
    total: int             # Ej: 50
    tendencia: str         # Ej: "+12% esta semana"

class RendimientoCategoriaSchema(BaseModel):
    categoria:str
    total_tareas:int
    tiempo_estimado_prom:float
    tiempo_real_prom:float
    dificultad_estimada_prom:float
    dificultad_real_prom:Optional[float]=None
    estado:Literal["eficiente","deficiente","insuficiente"]
    mejora_tiempo:Optional[Literal["mejora","estable","empeora"]]=None
    variacion_tiempo_pct: Optional[float]=None
    recomendacion:Literal["subir","mantener","bajar","sin_datos"]

class ResumenEstadisticasResponse(BaseModel):
    meta_semanal: MetaSemanalSchema
    categorias:list[RendimientoCategoriaSchema]