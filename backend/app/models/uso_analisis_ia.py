from sqlalchemy import CheckConstraint, Column, Date, Integer, String

from app.db.base import Base


class UsoAnalisisIA(Base):
    """Contadores diarios, sin guardar documentos ni resultados de Gemini."""

    __tablename__ = "uso_analisis_ia"

    fecha_utc = Column(Date, primary_key=True)
    alcance = Column(String(10), primary_key=True)
    identificador_alcance = Column(String(64), primary_key=True)
    cantidad = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("cantidad >= 0", name="ck_uso_analisis_ia_cantidad"),
        CheckConstraint(
            "(alcance = 'usuario' AND identificador_alcance <> '') "
            "OR (alcance = 'global' AND identificador_alcance = 'global')",
            name="ck_uso_analisis_ia_alcance",
        ),
    )
