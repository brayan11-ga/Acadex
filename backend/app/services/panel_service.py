# app/services/panel_service.py
from sqlalchemy.orm import Session
from datetime import datetime
from app.repositories.panel_repository import panel_repository
from app.schemas.panel_schema import DatosPanelResponse, TareaPanelSchema, ProgresoDiarioSchema, DiaProgresoSchema

class PanelService:
    def _formatear_fecha(self, fecha: datetime) -> str:
        """Da formato amigable a la fecha de vencimiento."""
        if not fecha:
            return ""
        
        hoy = datetime.now().date()
        fecha_tarea = fecha.date()
        delta = (fecha_tarea - hoy).days
        
        hora = fecha.strftime('%H:%M')
        
        if delta == 0:
            return f"Hoy, {hora}"
        elif delta == 1:
            return f"Mañana, {hora}"
        elif delta < 0:
            return f"Vencida (Hace {abs(delta)} días)"
        
        return f"{fecha.strftime('%d/%m/%Y')} {hora}"

    def obtener_datos_panel(self, db: Session, id_usuario: int) -> DatosPanelResponse:
        # 1. Procesar la Tarea Prioritaria
        tupla_prioritaria = panel_repository.obtener_tarea_prioritaria(db, id_usuario)
        tarea_prioritaria = None
        exclude_id = None
        
        if tupla_prioritaria:
            tarea_db, nombre_categoria = tupla_prioritaria
            exclude_id = tarea_db.id_tarea
            tarea_prioritaria = TareaPanelSchema(
                id=tarea_db.id_tarea,
                titulo=tarea_db.nombre,
                descripcion=tarea_db.descripcion,
                estado=tarea_db.estado,
                fechaVencimiento=self._formatear_fecha(tarea_db.fecha_entrega),
                etiqueta=nombre_categoria.upper()
            )

        # 2. Procesar las Próximas Tareas
        tuplas_proximas = panel_repository.obtener_proximas_tareas(db, id_usuario, exclude_id)
        proximas_tareas = []
        
        for tarea_db, nombre_categoria in tuplas_proximas:
            proximas_tareas.append(TareaPanelSchema(
                id=tarea_db.id_tarea,
                titulo=tarea_db.nombre,
                descripcion=tarea_db.descripcion,
                estado=tarea_db.estado,
                fechaVencimiento=self._formatear_fecha(tarea_db.fecha_entrega),
                etiqueta=nombre_categoria.upper()
            ))

        # 3. Procesar el Progreso Diario
        historial = panel_repository.obtener_historial_semana(db, id_usuario)
        pendientes = panel_repository.contar_tareas_pendientes(db, id_usuario)
        
        completadas_total = len(historial)
        total_tareas = completadas_total + pendientes

        # Mapear los días de la semana (0=LUN, 1=MAR, ..., 6=DOM)
        nombres_dias = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
        conteo_dias = {i: 0 for i in range(7)}
        
        for registro in historial:
            if registro.fechahora_fin:
                conteo_dias[registro.fechahora_fin.weekday()] += 1

        hoy_weekday = datetime.now().weekday()
        dias_progreso = []
        
        # Generar la lista para el frontend limitando a la semana de lunes a domingo
        for i in range(7):
            dias_progreso.append(DiaProgresoSchema(
                dia=nombres_dias[i],
                cantidad=conteo_dias[i],
                actual=(i == hoy_weekday)
            ))

        progreso = ProgresoDiarioSchema(
            completadas=completadas_total,
            total=total_tareas,
            dias=dias_progreso
        )

        # Retornar el objeto consolidado final
        return DatosPanelResponse(
            tareaPrioritaria=tarea_prioritaria,
            progreso=progreso,
            proximasTareas=proximas_tareas
        )

panel_service = PanelService()