# app/repositories/panel_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import asc
from datetime import datetime, timedelta

# Importamos directamente las CLASES
from app.models.tarea import Tarea
from app.models.categoria import Categoria
from app.models.historial_tarea import HistorialTarea

class PanelRepository:
    def obtener_tarea_prioritaria(self, db: Session, id_usuario: int):
        """
        Obtiene la tarea pendiente más urgente (por prioridad y fecha de entrega) 
        junto con el nombre de su categoría.
        """
        # Todo con T mayúscula y C mayúscula
        return db.query(Tarea, Categoria.nombre_categoria)\
            .join(Categoria, Tarea.id_categoria == Categoria.id_categoria)\
            .filter(Tarea.id_usuario == id_usuario, Tarea.estado == 'pendiente')\
            .order_by(asc(Tarea.prioridad), asc(Tarea.fecha_entrega))\
            .first()

    def obtener_proximas_tareas(self, db: Session, id_usuario: int, exclude_id: int = None, limit: int = 3):
        """
        Obtiene las siguientes tareas pendientes, excluyendo la prioritaria si existe.
        """
        query = db.query(Tarea, Categoria.nombre_categoria)\
            .join(Categoria, Tarea.id_categoria == Categoria.id_categoria)\
            .filter(Tarea.id_usuario == id_usuario, Tarea.estado == 'pendiente')
        
        if exclude_id:
            query = query.filter(Tarea.id_tarea != exclude_id)
            
        return query.order_by(asc(Tarea.fecha_entrega)).limit(limit).all()

    def obtener_historial_semana(self, db: Session, id_usuario: int):
        """
        Obtiene las tareas completadas en los últimos 7 días para armar el gráfico.
        """
        hace_una_semana = datetime.now() - timedelta(days=7)
        return db.query(HistorialTarea)\
            .filter(HistorialTarea.id_usuario == id_usuario, HistorialTarea.fechahora_fin >= hace_una_semana)\
            .all()

    def contar_tareas_pendientes(self, db: Session, id_usuario: int):
        """
        Cuenta cuántas tareas le faltan al usuario por completar en total.
        """
        return db.query(Tarea)\
            .filter(Tarea.id_usuario == id_usuario, Tarea.estado == 'pendiente')\
            .count()

panel_repository = PanelRepository()