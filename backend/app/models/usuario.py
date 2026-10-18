from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Identity, text
from sqlalchemy.sql import func
from app.db.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, Identity(always=True), primary_key=True)
    correo_electronico = Column(String(100), nullable=False, unique=True)
    contrasena = Column(String(60), nullable=False)
    fecha_registro = Column(Date, nullable=False, server_default=func.current_date())
    es_admin = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    intentos_fallidos = Column(Integer, nullable=False, default=0, server_default=text("0"))
    bloqueado = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    bloqueado_hasta = Column(DateTime, nullable=True)
