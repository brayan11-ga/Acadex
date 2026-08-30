from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, CheckConstraint
from app.db.base import Base

class SesionCronometro(Base):
    __tablename__ = "sesiones_cronometro"

    id_sesion = Column(Integer, primary_key=True, index=True)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime)
    duracion = Column(Float)
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        CheckConstraint("duracion is null or duracion >= 0", name="chk_duracion_sesion"),
        CheckConstraint("fecha_fin is null or fecha_fin >= fecha_inicio", name="chk_fechas_sesion"),
    )