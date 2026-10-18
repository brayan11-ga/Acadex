from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Identity, Index, Integer, String, func
from app.db.base import Base

class Archivo(Base):
    __tablename__ = "archivos"

    id_archivo = Column(Integer, Identity(always=True), primary_key=True)
    nombre = Column(String(100), nullable=False)
    tamano = Column(BigInteger)
    tipo = Column(String(10), nullable=False)
    fecha_adjuncion = Column(DateTime, nullable=False, server_default=func.now())
    ruta = Column(String(255), nullable=False)
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=False)
    id_usuario_subida = Column(
        Integer,
        ForeignKey("usuarios.id_usuario", ondelete="SET NULL"),
        nullable=True,
        comment="Usuario autenticado que subió el adjunto; NULL identifica registros históricos sin autor verificable.",
    )

    __table_args__ = (
        CheckConstraint("tamano is null or tamano >= 0", name="chk_tamano_archivo"),
        CheckConstraint("tipo IN ('PDF', 'DOCX', 'JPG', 'PNG')", name="chk_tipo_archivo"),
        Index("idx_archivos_tarea", "id_tarea"),
    )
