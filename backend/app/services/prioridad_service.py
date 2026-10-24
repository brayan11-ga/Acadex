# prioridad_service
import math
from statistics import mean
from sqlalchemy import func
from datetime import datetime, time
from app.repositories import prioridad_repository

VENTANA=10
MIN_HISTORIAL=3
UMBRAL_TIEMPO=0.20 #20% de la desviacion
UMBRAL_DIFICULTAD=1.0 #mas 1 punto de la dificultad

def prioridad_por_fecha(fecha_entrega,ahora:datetime | None=None)->int:
    if not isinstance(fecha_entrega,datetime):
        fecha_entrega=datetime.combine(fecha_entrega,time.max)
    ahora=ahora or datetime.now(fecha_entrega.tzinfo)
    dias=(fecha_entrega-ahora).total_seconds()/86400
    if dias<=1:
        return 5
    if dias<=3:
        return 4
    if dias<=7:
        return 3
    if dias <=14:
        return 2
    return 1

def calcular_prioridad(fecha_entrega:datetime, dificultad_estimada:int,historial:list[dict],es_primera:bool=False,)->int:
    if es_primera:
        return 5

    base=prioridad_por_fecha(fecha_entrega)
    historial=[h for h in historial[:VENTANA] if h["tiempo_estimado"]]
    n = len(historial)
    if n<MIN_HISTORIAL:
        return base
    dev_tiempo=mean((h["tiempo_real"]-h["tiempo_estimado"])/h["tiempo_estimado"] for h in historial)
    dif_real=[h["dificultad_real"] for h in historial if h["dificultad_real"]is not None]
    dev_dif=(mean(dif_real)-dificultad_estimada) if dif_real else 0

    senal_t =1 if dev_tiempo>UMBRAL_TIEMPO else -1 if dev_tiempo< -UMBRAL_TIEMPO else 0
    senal_d =1 if dev_dif>= UMBRAL_DIFICULTAD else -1 if dev_dif <= -UMBRAL_DIFICULTAD else 0
    ajuse =max (-1,min(1, senal_t+senal_d))

    peso=n / VENTANA
    return max(1,min(5, math.floor(base+ajuse*peso+0.5)))

def _calcular_para(db,tarea,es_primera=False)->int:
    historial=prioridad_repository.obtener_historial(
        db,tarea.id_categoria,tarea.id_usuario,tarea.id_grupo
    )
    return calcular_prioridad(tarea.fecha_entrega,tarea.dificultad_estimada, historial, es_primera)

def asignar_prioridad_inicial(db,tarea)->None:
    es_primera=prioridad_repository.contar_tareas(db, tarea.id_usuario, tarea.id_grupo, tarea.id_tarea) ==0 
    tarea.prioridad = _calcular_para(db, tarea, es_primera)
    
def recalcular_pendientes(db,id_categoria,id_usuario,id_grupo)->None:
    for t in prioridad_repository.obtener_pendientes(db, id_categoria, id_usuario, id_grupo):
        t.prioridad=_calcular_para(db,t)