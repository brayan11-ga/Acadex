from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, text

from app.db.base import Base


class LimiteSolicitud(Base):
    """Contadores temporales compartidos de peticiones, sin guardar IP o correo."""

    __tablename__ = "limites_solicitud"

    alcance = Column(String(40), primary_key=True)
    clave_hash = Column(String(64), primary_key=True)
    inicio_ventana = Column(DateTime, nullable=False)
    cantidad = Column(Integer, nullable=False, default=0, server_default=text("0"))

    __table_args__ = (
        CheckConstraint("cantidad >= 0", name="ck_limites_solicitud_cantidad"),
    )
