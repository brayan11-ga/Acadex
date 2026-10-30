# models/Perfil
from sqlalchemy import Column, Boolean, CheckConstraint, ForeignKey, Identity, Integer, String, Text, text
from app.db.base import Base

class Perfil(Base):
    __tablename__ = "perfiles"

    id_perfil = Column(Integer, Identity(always=True), primary_key=True)
    nombre_usuario = Column(String(50), nullable=False)
    telefono = Column(String(20))
    foto_perfil = Column(String(255))
    descripcion = Column(Text)
    notif_activas = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    limite_cronometro = Column(Integer,nullable=False, server_default="30")
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("limite_cronometro is null or limite_cronometro > 0", name="chk_limite_cronometro"),
    )
