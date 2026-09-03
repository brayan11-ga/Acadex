from sqlalchemy import Column, Integer, Float, ForeignKey, CheckConstraint
from app.db.base import Base

class EstadisticaCategoriaGrupo(Base):
    __tablename__ = "estadistica_categoria_grupo"

    id_estadistica_grupo = Column(Integer, primary_key=True, index=True)
    promedio_tiempo = Column(Float)
    promedio_dificultad = Column(Float)
    total_tareas = Column(Integer)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        CheckConstraint("total_tareas is null or total_tareas >= 0", name="chk_total_tareas_grupo"),
        CheckConstraint("promedio_dificultad is null or promedio_dificultad BETWEEN 1 AND 5", name="chk_promedio_dificultad_grupo"),
    )