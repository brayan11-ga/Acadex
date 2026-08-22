# app/models/tarea.py
from sqlalchemy import (
    Column, Integer, String, Text, TIMESTAMP, Boolean, Float,
    ForeignKey, CheckConstraint
)

from app.db.base import Base


class Tarea(Base):
    __tablename__ = "tareas"

    id_tarea = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_entrega = Column(TIMESTAMP, nullable=False)
    estado = Column(String(50), nullable=False, default="pendiente")
    dificultad_estimada = Column(Integer, nullable=False)
    tiempo_estimado = Column(Integer, nullable=False)
    prioridad = Column(Integer, nullable=True)
    tiempo_acumulado = Column(Float, nullable=False, default=0)
    cronometro_activo = Column(Boolean, nullable=False, default=False)
    ultima_pausa = Column(TIMESTAMP, nullable=True)

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"), nullable=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)

    __table_args__ = (
        CheckConstraint("dificultad_estimada BETWEEN 1 AND 5", name="chk_dificultad_estimada"),
        CheckConstraint("tiempo_estimado > 0", name="chk_tiempo_estimado"),
        CheckConstraint("prioridad IS NULL OR prioridad > 0", name="chk_prioridad"),
        CheckConstraint(
            "(id_usuario IS NOT NULL AND id_grupo IS NULL) OR "
            "(id_usuario IS NULL AND id_grupo IS NOT NULL)",
            name="chk_tarea_owner",
        ),
    )