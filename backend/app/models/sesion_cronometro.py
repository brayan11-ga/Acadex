from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Identity, Index, Integer, REAL, text
from app.db.base import Base

class SesionCronometro(Base):
    __tablename__ = "sesiones_cronometro"

    id_sesion = Column(Integer, Identity(always=True), primary_key=True)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime)
    duracion = Column(REAL)
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        CheckConstraint("duracion is null or duracion >= 0", name="chk_duracion_sesion"),
        CheckConstraint("fecha_fin is null or fecha_fin >= fecha_inicio", name="chk_fechas_sesion"),
        Index(
            "uq_sesiones_tarea_activa",
            "id_tarea",
            unique=True,
            postgresql_where=text("fecha_fin IS NULL"),
            sqlite_where=text("fecha_fin IS NULL"),
        ),
        Index("idx_sesiones_tarea", "id_tarea"),
        Index("idx_sesiones_usuario", "id_usuario"),
    )
