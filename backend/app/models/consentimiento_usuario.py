from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.db.base import Base


class ConsentimientoUsuario(Base):
    __tablename__ = "consentimientos_usuario"

    id_consentimiento = Column(Integer, Identity(always=False), primary_key=True)
    id_usuario = Column(
        Integer,
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    tipo_consentimiento = Column(String(40), nullable=False)
    version_politica = Column(String(30), nullable=False)
    fecha_aceptacion = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "tipo_consentimiento IN ('tratamiento_datos', 'aviso_almacenamiento')",
            name="chk_consentimientos_usuario_tipo",
        ),
        UniqueConstraint(
            "id_usuario",
            "tipo_consentimiento",
            "version_politica",
            name="uq_consentimientos_usuario_version",
        ),
        {
            "comment": (
                "Evidencia versionada de autorización de tratamiento de datos y "
                "lectura del aviso de almacenamiento local."
            )
        },
    )
