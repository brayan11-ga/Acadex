# app/repositories/estadisticas_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models.tarea import Tarea
from app.models.historial_tarea import HistorialTarea
from app.models.categoria import Categoria

class EstadisticasRepository:
    def obtener_historial_rango(self, db: Session, id_usuario: int, fecha_inicio: datetime, fecha_fin: datetime):
        """
        Obtiene todas las tareas completadas en un rango de fechas.
        Hace un JOIN con Tarea y Categoria para traer toda la info junta (tiempos, nombres, etc).
        """
        return db.query(HistorialTarea, Tarea, Categoria)\
            .join(Tarea, HistorialTarea.id_tarea == Tarea.id_tarea)\
            .join(Categoria, Tarea.id_categoria == Categoria.id_categoria)\
            .filter(
                HistorialTarea.id_usuario == id_usuario,
                HistorialTarea.fechahora_fin >= fecha_inicio,
                HistorialTarea.fechahora_fin <= fecha_fin
            ).all()

    def contar_tareas_esperadas_rango(self, db: Session, id_usuario: int, fecha_inicio: datetime, fecha_fin: datetime):
        """
        Cuenta cuántas tareas tenían fecha de entrega en esta semana (estén completadas o no).
        Esto nos sirve para calcular la "Meta Semanal" (ej: hiciste 41 de 50 tareas esperadas).
        """
        return db.query(Tarea)\
            .filter(
                Tarea.id_usuario == id_usuario,
                Tarea.fecha_entrega >= fecha_inicio,
                Tarea.fecha_entrega <= fecha_fin
            ).count()

estadisticas_repository = EstadisticasRepository()