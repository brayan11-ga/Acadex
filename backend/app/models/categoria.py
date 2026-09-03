from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre_categoria = Column(String(50), nullable=False, unique=True)