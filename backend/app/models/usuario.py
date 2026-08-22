# app/models/usuario.py
from sqlalchemy import Column, Integer, String, Boolean, Date

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    correo_electronico = Column(String(100), nullable=False, unique=True)
    contrasena = Column(String(60), nullable=False)
    fecha_registro = Column(Date, nullable=False)
    es_admin = Column(Boolean, nullable=False, default=False)