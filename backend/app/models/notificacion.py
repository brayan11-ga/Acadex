from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from app.db.base import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id_notificacion = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(50), nullable=False)
    detalles = Column(String(100))
    fecha_envio = Column(DateTime, nullable=False, server_default=func.now())
    estado = Column(Boolean, nullable=False, default=False)
    tipo = Column(String(50), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=True)