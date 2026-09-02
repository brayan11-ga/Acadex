from sqlalchemy import (Column, Integer, String, Date, ForeignKey,
    CheckConstraint, UniqueConstraint, func)
from app.db.base import Base

class Integrante(Base):
    __tablename__ = "integrantes"

    id_integrante = Column(Integer, primary_key=True, index=True)
    rol = Column(String(50), nullable=False)
    fecha_ingreso = Column(Date, nullable=False, server_default=func.current_date())
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        CheckConstraint("rol IN ('lider', 'miembro')", name="chk_rol_integrante"),
        UniqueConstraint("id_usuario", "id_grupo", name="uq_usuario_grupo"),
    )