# prioridad_service
import math
from statistics import mean
from datetime import datetime, time
from app.repositories import prioridad_repository

VENTANA=10
MIN_HISTORIAL=3
SEGUNDOS_POR_MINUTOS=60
UMBRAL_SCORE=[(1.0,5),(0.8,4),(0.6,3),(0.4,2)] #mas 1 punto de la dificultad
FACTOR_TIEMPO_MIN = 0.5  # el tiempo efectivo nunca baja de la mitad de lo estimado
FACTOR_TIEMPO_MAX = 3.0  # ni pasa del triple

def _minutos_restantes(fecha_entrega,ahora:datetime | None =None)->float:
    if not isinstance(fecha_entrega,datetime):
        fecha_entrega=datetime.combine(fecha_entrega,time.max)
    ahora=ahora or datetime.now(fecha_entrega.tzinfo)
    return (fecha_entrega-ahora).total_seconds()/60

def _valores_efectivos(tiempo_estimado:int, dificultad_estimada:int, historial: list[dict]):
    muestra=[h for h in historial[:VENTANA] 
            if h["tiempo_estimado"] and h["tiempo_real"]and h["tiempo_real"]>0
            ]
    if len(muestra)<MIN_HISTORIAL:
        return tiempo_estimado,dificultad_estimada

    factor=(
        mean(h["tiempo_real"]/SEGUNDOS_POR_MINUTOS for h in muestra)/ mean(h["tiempo_estimado"] for h in muestra)
    )
    factor = max(FACTOR_TIEMPO_MIN, min(FACTOR_TIEMPO_MAX, factor))
    tiempo_efectivo=tiempo_estimado*factor

    con_dif=[h for h in muestra if h["dificultad_real"] is not None]
    if con_dif:
        sesgo=(mean(h["dificultad_real"]for h in con_dif)-mean(h["dificultad_estimada"] for h in con_dif)
        )
        dificultad_efectiva=max(1, min (5,math.floor(dificultad_estimada + sesgo + 0.5)))
    else:
        dificultad_efectiva=dificultad_estimada
    return tiempo_efectivo, dificultad_efectiva

def calcular_prioridad(fecha_entrega:datetime,tiempo_estimado:int, dificultad_estimada:int,historial:list[dict],es_primera:bool=False,ahora:datetime|None=None,)->int:
    if es_primera:
        return 5

    tiempo_ef, dif_ef=_valores_efectivos(tiempo_estimado,dificultad_estimada,historial)
    restantes=_minutos_restantes(fecha_entrega, ahora)

    if restantes<=tiempo_ef:
        return 5
    
    score=(tiempo_ef/restantes)*(1+dif_ef /10)
    for minimo, prioridad in UMBRAL_SCORE:
        if score>=minimo:
            return prioridad
    return 1

def _calcular_para(db,tarea,es_primera=False)->int:
    historial=prioridad_repository.obtener_historial(
        db,tarea.id_categoria,tarea.id_usuario,tarea.id_grupo
    )
    return calcular_prioridad(tarea.fecha_entrega,tarea.tiempo_estimado,tarea.dificultad_estimada, historial, es_primera)

def asignar_prioridad_inicial(db,tarea)->None:
    es_primera=prioridad_repository.contar_tareas(db, tarea.id_usuario, tarea.id_grupo, tarea.id_tarea) ==0 
    tarea.prioridad = _calcular_para(db, tarea, es_primera)
    
def recalcular_pendientes(db,id_categoria,id_usuario,id_grupo)->None:
    for t in prioridad_repository.obtener_pendientes(db, id_categoria, id_usuario, id_grupo):
        t.prioridad=_calcular_para(db,t)

def recaulcular_tarea(db,tarea)->None:
    tarea.prioridad=_calcular_para(db, tarea)

def calcular_dificultad_real(dificultad_estimada:int, tiempo_estimado:int, tiempo_real:float | None)->int:
    # sin timpos registrados no se podra medir, se conservara la estimacion
    if not tiempo_real or tiempo_real <= 0 or not tiempo_estimado:
        return dificultad_estimada
    minutos_reales=tiempo_real / SEGUNDOS_POR_MINUTOS
    valor=dificultad_estimada*minutos_reales/tiempo_estimado
    return max(1, min(5, math.floor(valor+0.5)))

def recalcular_visibles(db, tareas) -> None:
    historiales = {}
    for t in tareas:
        if (t.estado or "").lower() == "completada":
            continue
        clave = (t.id_categoria, t.id_usuario, t.id_grupo)
        if clave not in historiales:
            historiales[clave] = prioridad_repository.obtener_historial(db, *clave)
        t.prioridad = calcular_prioridad(
            t.fecha_entrega, t.tiempo_estimado, t.dificultad_estimada, historiales[clave]
        )