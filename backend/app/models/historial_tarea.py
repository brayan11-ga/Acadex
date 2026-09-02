from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, CheckConstraint, func
from app.db.base import Base

class HistorialTarea(Base):
    __tablename__ = "historial_tareas"

    id_historial = Column(Integer, primary_key=True, index=True)
    fechahora_fin = Column(DateTime, nullable=False, server_default=func.now())
    tiempo_real = Column(Float)
    dificultad_real = Column(Integer)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=False)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"), nullable=True)

    __table_args__ = (
        CheckConstraint("dificultad_real is null or dificultad_real BETWEEN 1 AND 5", name="chk_dificultad_real"),
        CheckConstraint("tiempo_real is null or tiempo_real >= 0", name="chk_tiempo_real"),
    )