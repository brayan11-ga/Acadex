# app/repositories/estadisticas_repository.py
from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.tarea import Tarea
from app.models.historial_tarea import HistorialTarea
from app.models.categoria import Categoria

class EstadisticasRepository:
    def obtener_historial_rango(self, db:Session, id_usuario: int, fecha_inicio: datetime, fecha_fin: datetime):
        return db.query(HistorialTarea, Tarea, Categoria)\
            .join(Tarea, HistorialTarea.id_tarea == Tarea.id_tarea)\
            .join(Categoria, Tarea.id_categoria == Categoria.id_categoria)\
            .filter(
                HistorialTarea.id_usuario == id_usuario,
                HistorialTarea.fechahora_fin >= fecha_inicio,
                HistorialTarea.fechahora_fin <= fecha_fin
            ).all()

    def contar_tareas_esperadas_rango(self, db:Session, id_usuario:int , fecha_inicio:datetime, fecha_fin:datetime):
        return db.query(Tarea)\
        .filter(
            Tarea.id_usuario==id_usuario,
            Tarea.fecha_entrega>=fecha_inicio,
            Tarea.fecha_entrega<=fecha_fin
        ).count()

    def obtener_ultimas_por_categoria(self,db:Session,id_usuario:int,limite:int):
        posicion=func.row_number().over(
            partition_by=Tarea.id_categoria,
            order_by=HistorialTarea.fechahora_fin.desc(),
        ).label("posicion")

        ranking=(
            select(HistorialTarea.id_historial.label("id_historial"),posicion)
            .join(Tarea, Tarea.id_tarea==HistorialTarea.id_tarea)
            .where(
                HistorialTarea.id_usuario==id_usuario,
                HistorialTarea.id_grupo.is_(None),
                HistorialTarea.tiempo_real.is_not(None),
            )
            .subquery()
        )
        consulta=(
            select(HistorialTarea,Tarea, Categoria)
            .join(ranking,ranking.c.id_historial==HistorialTarea.id_historial)
            .join(Tarea,Tarea.id_tarea==HistorialTarea.id_tarea)
            .join(Categoria,Categoria.id_categoria==Tarea.id_categoria)
            .where(ranking.c.posicion<=limite)
            .order_by(Categoria.nombre_categoria,HistorialTarea.fechahora_fin.desc())
            )
        return db.execute(consulta).all()

estadisticas_repository=EstadisticasRepository()