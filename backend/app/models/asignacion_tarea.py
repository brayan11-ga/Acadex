from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from app.db.base import Base

class AsignacionTarea(Base):
    __tablename__ = "asignacion_tareas"

    id_asignacion = Column(Integer, primary_key=True, index=True)
    fecha_asignacion = Column(DateTime, nullable=False, server_default=func.now())
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=False)
    id_integrante = Column(Integer, ForeignKey("integrantes.id_integrante", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_tarea", "id_integrante", name="uq_tarea_integrante"),
    )