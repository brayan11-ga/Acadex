from sqlalchemy import Column, DateTime, ForeignKey, Identity, Index, Integer, UniqueConstraint, func
from app.db.base import Base

class AsignacionTarea(Base):
    __tablename__ = "asignacion_tareas"

    id_asignacion = Column(Integer, Identity(always=True), primary_key=True)
    fecha_asignacion = Column(DateTime, nullable=False, server_default=func.now())
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=False)
    id_integrante = Column(Integer, ForeignKey("integrantes.id_integrante", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_tarea", "id_integrante", name="uq_tarea_integrante"),
        Index("idx_asignacion_integrante", "id_integrante"),
        Index("idx_asignacion_tarea", "id_tarea"),
    )
