# models/Notificacion
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Identity, Index, Integer, String, func, text
from app.db.base import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id_notificacion = Column(Integer, Identity(always=True), primary_key=True)
    titulo = Column(String(50), nullable=False)
    detalles = Column(String(100))
    fecha_envio = Column(DateTime, nullable=False, server_default=func.now())
    estado = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    tipo = Column(String(50), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=True)

    __table_args__ = (
        Index("idx_notificaciones_tarea", "id_tarea"),
        Index("idx_notificaciones_usuario", "id_usuario"),
    )
