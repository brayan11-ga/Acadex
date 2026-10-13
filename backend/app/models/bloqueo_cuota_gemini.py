from sqlalchemy import Column, DateTime, String

from app.db.base import Base


class BloqueoCuotaGemini(Base):
    """Bloqueo compartido entre instancias mientras Google repone la cuota diaria."""

    __tablename__ = "bloqueo_cuota_gemini"

    id = Column(String(32), primary_key=True)
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=False)
