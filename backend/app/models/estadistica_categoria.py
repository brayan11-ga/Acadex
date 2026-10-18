from sqlalchemy import CheckConstraint, Column, ForeignKey, Identity, Integer, REAL
from app.db.base import Base

class EstadisticaCategoria(Base):
    __tablename__ = "estadistica_categoria"

    id_estadistica_categoria = Column(Integer, Identity(always=True), primary_key=True)
    promedio_tiempo = Column(REAL)
    promedio_dificultad = Column(REAL)
    total_tareas = Column(Integer)
    id_perfil = Column(Integer, ForeignKey("perfiles.id_perfil", ondelete="CASCADE"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        CheckConstraint("total_tareas is null or total_tareas >= 0", name="chk_total_tareas"),
        CheckConstraint("promedio_dificultad is null or promedio_dificultad BETWEEN 1 AND 5", name="chk_promedio_dificultad"),
    )
