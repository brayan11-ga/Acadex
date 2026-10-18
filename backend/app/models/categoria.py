from sqlalchemy import Column, Identity, Integer, String
from app.db.base import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, Identity(always=True), primary_key=True)
    nombre_categoria = Column(String(50), nullable=False, unique=True)
