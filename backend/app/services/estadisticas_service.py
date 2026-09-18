# app/services/estadisticas_service.py
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session

from app.repositories.estadisticas_repository import estadisticas_repository
from app.schemas.estadisticas_schema import (
    ResumenEstadisticasResponse,
    MetaSemanalSchema,
    DiaEstadisticaSchema,
    FocusScoreSchema,
    CategoriaTopSchema,
    PromedioTiempoSchema,
    InsightSchema
)

def obtener_resumen_estadisticas(db: Session, id_usuario: int) -> ResumenEstadisticasResponse:
    # 1. Definimos la ventana de tiempo (últimos 7 días)
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=7)

    # 2. Obtenemos datos crudos
    historial = estadisticas_repository.obtener_historial_rango(db, id_usuario, fecha_inicio, fecha_fin)
    total_esperadas = estadisticas_repository.contar_tareas_esperadas_rango(db, id_usuario, fecha_inicio, fecha_fin)

    # Variables auxiliares para los cálculos dinámicos
    nombres_dias = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
    conteo_dias = {i: 0 for i in range(7)}
    
    total_tiempo_real = 0
    tareas_a_tiempo = 0
    conteo_categorias = defaultdict(float) # Para sumar horas por categoría
    conteo_horas_dia = defaultdict(int)    # Para saber a qué hora trabaja más

    # 3. Procesamiento central (Un solo ciclo for recorre todo)
    for reg_historial, reg_tarea, reg_categoria in historial:
        # Gráfico diario
        dia_idx = reg_historial.fechahora_fin.weekday()
        conteo_dias[dia_idx] += 1
        
        # Pico de rendimiento (Insights)
        hora = reg_historial.fechahora_fin.hour
        conteo_horas_dia[hora] += 1

        # Tiempos (Usamos el tiempo real de la sesión, o el estimado si no usó cronómetro)
        tiempo_real = reg_historial.tiempo_real or reg_tarea.tiempo_estimado or 0
        tiempo_estimado = reg_tarea.tiempo_estimado or 0

        total_tiempo_real += tiempo_real

        # Focus Score (Gana puntos si terminó más rápido o igual al tiempo estimado)
        if tiempo_real <= tiempo_estimado:
            tareas_a_tiempo += 1

        # Sumar horas a la categoría correspondiente
        conteo_categorias[reg_categoria.nombre_categoria] += (tiempo_real / 60)

    # 4. Cálculo de Meta Semanal
    completadas = len(historial)
    total_meta = total_esperadas if total_esperadas > completadas else completadas
    porcentaje = int((completadas / total_meta) * 100) if total_meta > 0 else 0

    # 5. Formateo del Gráfico
    dia_actual_idx = fecha_fin.weekday()
    grafico_diario = [
        DiaEstadisticaSchema(
            dia=nombres_dias[i],
            cantidad=conteo_dias[i],
            actual=(i == dia_actual_idx)
        ) for i in range(7)
    ]

    # 6. Cálculo de Top Category
    categoria_top_nombre = "Sin datos"
    categoria_top_horas = 0.0
    if conteo_categorias:
        categoria_top_nombre = max(conteo_categorias, key=conteo_categorias.get)
        categoria_top_horas = round(conteo_categorias[categoria_top_nombre], 1)

    # 7. Promedios y Focus Score
    promedio_minutos = int(total_tiempo_real / completadas) if completadas > 0 else 0
    focus_score = int((tareas_a_tiempo / completadas) * 100) if completadas > 0 else 0
    # Dar un bono de gracia mínimo para que no se vea en 0 al iniciar
    focus_score = max(60, focus_score) if completadas > 0 else 0

    # 8. Generación del Insight (El texto dinámico de eficiencia)
    insights = []
    if conteo_horas_dia:
        hora_pico = max(conteo_horas_dia, key=conteo_horas_dia.get)
        insights.append(InsightSchema(
            titulo="Pico de Rendimiento Detectado",
            descripcion=f"Tu tasa de completitud es mayor alrededor de las {hora_pico}:00. ¡Agenda tus tareas más difíciles en este horario!"
        ))
    else:
        insights.append(InsightSchema(
            titulo="Eficiencia en Análisis",
            descripcion="Completa más tareas con el cronómetro para descubrir tus mejores horarios."
        ))

    # 9. Construir y retornar el JSON final validado por Pydantic
    return ResumenEstadisticasResponse(
        meta_semanal=MetaSemanalSchema(
            porcentaje=porcentaje,
            completadas=completadas,
            total=total_meta,
            tendencia="En buen camino" if porcentaje >= 50 else "Necesita atención"
        ),
        grafico_diario=grafico_diario,
        focus_score=FocusScoreSchema(
            puntaje=focus_score,
            nivel="Nivel Élite" if focus_score >= 90 else "Nivel Óptimo" if focus_score >= 70 else "Nivel Base"
        ),
        categoria_top=CategoriaTopSchema(
            nombre=categoria_top_nombre,
            horas_dedicadas=categoria_top_horas
        ),
        promedio_tiempo=PromedioTiempoSchema(
            minutos=promedio_minutos,
            tendencia="Basado en los últimos 7 días"
        ),
        insights=insights,
        sugerencia_ia=InsightSchema(
            titulo="Sugerencia de IA (Fase 2)",
            descripcion="Aplica la técnica Pomodoro en tus ciclos de desarrollo para mantener la concentración constante y reducir la fatiga."
        )
    )