from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, CheckConstraint, func
from app.db.base import Base

class TokenTemporal(Base):
    __tablename__ = "tokens_temporales"

    id_token = Column(Integer, primary_key=True, index=True)
    tipo_token = Column(String(50), nullable=False)
    valor_token = Column(String(50), nullable=False, unique=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, nullable=False, default=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=True)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"), nullable=True)

    __table_args__ = (
        CheckConstraint("fecha_expiracion > fecha_creacion", name="chk_fecha_token"),
    )