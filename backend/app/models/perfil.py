from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, CheckConstraint
from app.db.base import Base

class Perfil(Base):
    __tablename__ = "perfiles"

    id_perfil = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(50), nullable=False)
    telefono = Column(String(20))
    foto_perfil = Column(String(255))
    descripcion = Column(Text)
    notif_activas = Column(Boolean, nullable=False, default=True)
    limite_cronometro = Column(Integer)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("limite_cronometro is null or limite_cronometro > 0", name="chk_limite_cronometro"),
    )