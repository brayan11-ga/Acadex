from sqlalchemy import Column, Date, Identity, Integer, String, Text, func
from app.db.base import Base

class Grupo(Base):
    __tablename__ = "grupos"

    id_grupo = Column(Integer, Identity(always=True), primary_key=True)
    nombre_grupo = Column(String(50), nullable=False)
    descripcion = Column(Text)
    codigo_acceso = Column(String(20), nullable=False, unique=True)
    fecha_creacion = Column(Date, nullable=False, server_default=func.current_date())
