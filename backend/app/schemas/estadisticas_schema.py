# app/schemas/estadisticas_schema.py
from pydantic import BaseModel
from typing import List, Optional

# 1. Bloque: Meta Semanal (Weekly Goal)
class MetaSemanalSchema(BaseModel):
    porcentaje: int        # Ej: 82
    completadas: int       # Ej: 41
    total: int             # Ej: 50
    tendencia: str         # Ej: "+12% esta semana"

# 2. Bloque: Gráfico de Tareas (Tasks Completed)
class DiaEstadisticaSchema(BaseModel):
    dia: str               # Ej: "MON", "TUE"
    cantidad: int          # Cantidad de tareas completadas
    actual: bool = False   # Para resaltar el día de hoy si lo deseas

# 3. Bloque: Tarjetas pequeñas de métricas (Focus, Top Category, Avg)
class FocusScoreSchema(BaseModel):
    puntaje: int           # Ej: 94
    nivel: str             # Ej: "Nivel Élite" o la flechita verde

class CategoriaTopSchema(BaseModel):
    nombre: str            # Ej: "Desarrollo Backend"
    horas_dedicadas: float # Ej: 18.5

class PromedioTiempoSchema(BaseModel):
    minutos: int           # Ej: 42
    tendencia: str         # Ej: "-8% (Más rápido)"

# 4. Bloque: Textos de Análisis (Efficiency Insights & AI Suggestion)
class InsightSchema(BaseModel):
    titulo: str            # Ej: "Pico de rendimiento detectado"
    descripcion: str       # Ej: "Tu tasa de completitud es 40% mayor en la mañana..."

# 5. EL ESQUEMA PRINCIPAL (El JSON final que agrupa todo)
class ResumenEstadisticasResponse(BaseModel):
    meta_semanal: MetaSemanalSchema
    grafico_diario: List[DiaEstadisticaSchema]
    focus_score: FocusScoreSchema
    categoria_top: CategoriaTopSchema
    promedio_tiempo: PromedioTiempoSchema
    insights: List[InsightSchema]
    sugerencia_ia: Optional[InsightSchema] = None # Opcional por si no hay datos para la IA