from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, CheckConstraint, func
from app.db.base import Base

class Archivo(Base):
    __tablename__ = "archivos"

    id_archivo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tamano = Column(BigInteger)
    tipo = Column(String(10), nullable=False)
    fecha_adjuncion = Column(DateTime, nullable=False, server_default=func.now())
    ruta = Column(String(255), nullable=False)
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        CheckConstraint("tamano is null or tamano >= 0", name="chk_tamano_archivo"),
        CheckConstraint("tipo IN ('PDF', 'DOCX', 'JPG', 'PNG')", name="chk_tipo_archivo"),
    )