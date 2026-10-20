from collections import defaultdict
from datetime import datetime,timedelta
from sqlalchemy.orm import Session
from app.repositories.estadisticas_repository import estadisticas_repository
from app.schemas.estadisticas_schema import (MetaSemanalSchema, RendimientoCategoriaSchema, ResumenEstadisticasResponse,)
MUESTRA_POR_CATEGORIA = 10   # RF-022
MIN_TAREAS_CATEGORIA = 3     # RF-024
UMBRAL_MEJORA = 0.10         # variación del 10 % para hablar de mejora o empeora
ORDEN_ESTADO = {"deficiente": 0, "eficiente": 1, "insuficiente": 2}


def _promedio(valores):
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else None


def _meta_semanal(db: Session, id_usuario: int) -> MetaSemanalSchema:
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=7)

    historial = estadisticas_repository.obtener_historial_rango(db, id_usuario, fecha_inicio, fecha_fin)
    total_esperadas = estadisticas_repository.contar_tareas_esperadas_rango(db, id_usuario, fecha_inicio, fecha_fin)

    completadas = len(historial)
    total = max(total_esperadas, completadas)
    porcentaje = int((completadas / total) * 100) if total > 0 else 0

    return MetaSemanalSchema(
        porcentaje=porcentaje,
        completadas=completadas,
        total=total,
        tendencia="En buen camino" if porcentaje >= 50 else "Necesita atención",
    )


def _evaluar_categoria(nombre: str, filas: list) -> RendimientoCategoriaSchema:
    # `filas` viene ordenada de la más reciente a la más antigua: [(historial, tarea), ...]
    tiempos_reales = [h.tiempo_real for h, _ in filas]
    tiempo_real = _promedio(tiempos_reales)
    tiempo_est = _promedio([t.tiempo_estimado for _, t in filas])
    dif_est = _promedio([t.dificultad_estimada for _, t in filas])
    dif_real = _promedio([h.dificultad_real for h, _ in filas])

    base = dict(
        categoria=nombre,
        total_tareas=len(filas),
        tiempo_estimado_prom=round(tiempo_est, 1),
        tiempo_real_prom=round(tiempo_real, 1),
        dificultad_estimada_prom=round(dif_est, 1),
        dificultad_real_prom=round(dif_real, 1) if dif_real is not None else None,
    )

    if len(filas) < MIN_TAREAS_CATEGORIA:
        return RendimientoCategoriaSchema(**base, estado="insuficiente", recomendacion="sin_datos")

    eficiente = tiempo_real <= tiempo_est and (dif_real is None or dif_real <= dif_est)

    # Mejora de tiempo: mitad más reciente vs. mitad anterior de la muestra
    mitad = len(tiempos_reales) // 2
    recientes = _promedio(tiempos_reales[:mitad])
    anteriores = _promedio(tiempos_reales[mitad:])
    mejora, variacion = None, None
    if recientes is not None and anteriores:
        variacion = (recientes - anteriores) / anteriores
        if variacion <= -UMBRAL_MEJORA:
            mejora = "mejora"
        elif variacion >= UMBRAL_MEJORA:
            mejora = "empeora"
        else:
            mejora = "estable"

    if eficiente and mejora != "empeora":
        recomendacion = "subir"
    elif not eficiente and mejora != "mejora":
        recomendacion = "bajar"
    else:
        recomendacion = "mantener"

    return RendimientoCategoriaSchema(
        **base,
        estado="eficiente" if eficiente else "deficiente",
        mejora_tiempo=mejora,
        variacion_tiempo_pct=round(variacion * 100, 1) if variacion is not None else None,
        recomendacion=recomendacion,
    )


def obtener_resumen_estadisticas(db: Session, id_usuario: int) -> ResumenEstadisticasResponse:
    filas = estadisticas_repository.obtener_ultimas_por_categoria(db, id_usuario, MUESTRA_POR_CATEGORIA)

    por_categoria = defaultdict(list)
    for historial, tarea, categoria in filas:
        por_categoria[categoria.nombre_categoria].append((historial, tarea))

    categorias = [_evaluar_categoria(nombre, f) for nombre, f in por_categoria.items()]
    categorias.sort(key=lambda c: (ORDEN_ESTADO[c.estado], c.categoria))

    return ResumenEstadisticasResponse(
        meta_semanal=_meta_semanal(db, id_usuario),
        categorias=categorias,
    )