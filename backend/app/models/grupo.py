from sqlalchemy import Column, Integer, String, Text, Date, func
from app.db.base import Base

class Grupo(Base):
    __tablename__ = "grupos"

    id_grupo = Column(Integer, primary_key=True, index=True)
    nombre_grupo = Column(String(50), nullable=False)
    descripcion = Column(Text)
    codigo_acceso = Column(String(20), nullable=False, unique=True)
    fecha_creacion = Column(Date, nullable=False, server_default=func.current_date())