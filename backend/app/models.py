from sqlalchemy import (
    Column, Integer, BigInteger, String, Date, Boolean, ForeignKey,
    DateTime, Float, Text, UniqueConstraint, CheckConstraint, func
)
from backend.app.databases import base


class Usuarios(base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    correo_electronico = Column(String(100), nullable=False, unique=True)
    contrasena = Column(String(60), nullable=False)
    fecha_registro = Column(Date, nullable=False, server_default=func.current_date())
    es_admin = Column(Boolean, nullable=False, default=False)


class Categorias(base):
    __tablename__ = "categorias"
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre_categoria = Column(String(50), nullable=False)


class Grupos(base):
    __tablename__ = "grupos"
    id_grupo = Column(Integer, primary_key=True, index=True)
    nombre_grupo = Column(String(50), nullable=False)
    descripcion = Column(Text)
    fecha_creacion = Column(Date, nullable=False)


class Integrantes(base):
    __tablename__ = "integrantes"
    id_integrante = Column(Integer, primary_key=True, index=True)
    rol = Column(String(50), nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        CheckConstraint("rol IN ('lider', 'miembro')", name="chk_rol_integrante"),
    )


class Tareas(base):
    __tablename__ = "tareas"
    id_tarea = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, index=True)
    fecha_entrega = Column(DateTime, nullable=False, index=True)
    estado = Column(String(50), nullable=False)
    dificultad_estimada = Column(Integer, nullable=False)
    tiempo_estimado = Column(Integer, nullable=False)
    prioridad = Column(Integer)
    tiempo_acumulado = Column(Float)
    cronometro_activo = Column(Boolean)
    ultima_pausa = Column(DateTime)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"), nullable=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "dificultad_estimada BETWEEN 1 AND 5", name="chk_dificultad_estimada"
        ),
        CheckConstraint(
            "(id_usuario IS NOT NULL AND id_grupo IS NULL) OR "
            "(id_usuario IS NULL AND id_grupo IS NOT NULL)",
            name="chk_tarea_owner",
        ),
    )


class AsignacionTareas(base):
    __tablename__ = "asignacion_tareas"
    id_asignacion = Column(Integer, primary_key=True, index=True)
    fecha_asignacion = Column(DateTime)
    id_tarea = Column(
        Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), unique=True
    )
    id_integrante = Column(
        Integer, ForeignKey("integrantes.id_integrante", ondelete="CASCADE")
    )


class Perfiles(base):
    __tablename__ = "perfiles"
    id_perfil = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(50), nullable=False)
    telefono = Column(String(20))
    foto_perfil = Column(String(255))
    descripcion = Column(Text)
    notif_activas = Column(Boolean, nullable=False, default=True)
    limite_cronometro = Column(Integer)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, unique=True)


class MetodosInicioSesion(base):
    __tablename__ = "metodos_inicio_sesion"
    id_metodo = Column(Integer, primary_key=True, index=True)
    tipo_metodo = Column(String(50), nullable=False)
    correo = Column(String(255))
    contrasena_hash = Column(String(255))
    token_google = Column(String(255))
    estado = Column(Boolean, nullable=False, default=True)
    fecha_vinculacion = Column(Date, nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)


class TokensTemporales(base):
    __tablename__ = "tokens_temporales"
    id_token = Column(Integer, primary_key=True, index=True)
    tipo_token = Column(String(50), nullable=False)
    valor_token = Column(String(50), nullable=False, unique=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, nullable=False, default=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"))


class Notificaciones(base):
    __tablename__ = "notificaciones"
    id_notificacion = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(50), nullable=False)
    detalles = Column(String(100))
    fecha_envio = Column(DateTime, nullable=False)
    estado = Column(Boolean, nullable=False, default=False)
    tipo = Column(String(50), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"))


class Archivos(base):
    __tablename__ = "archivos"
    id_archivo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    tamano = Column(BigInteger)
    tipo = Column(String(10), nullable=False)
    fecha_adjuncion = Column(DateTime, nullable=False)
    ruta = Column(String(255), nullable=False)
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"))
    id_integrante = Column(Integer, ForeignKey("integrantes.id_integrante"))
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('PDF', 'DOCX', 'JPG', 'PNG')", name="chk_tipo_archivo"),)


class HistorialTareas(base):
    __tablename__ = "historial_tareas"
    id_historial = Column(Integer, primary_key=True, index=True)
    fechahora_fin = Column(DateTime, nullable=False)
    tiempo_real = Column(Float)
    dificultad_real = Column(Integer)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_tarea = Column(Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"))
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"))

    __table_args__ = (CheckConstraint("dificultad_real BETWEEN 1 AND 5", name="chk_dificultad_real"),)


class EstadisticaCategoria(base):
    __tablename__ = "estadistica_categoria"
    id_estadistica_categoria = Column(Integer, primary_key=True, index=True)
    promedio_tiempo = Column(Float)
    promedio_dificultad = Column(Float)
    total_tareas = Column(Integer)
    id_perfil = Column(Integer, ForeignKey("perfiles.id_perfil"))
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))


class EstadisticaCategoriaGrupo(base):
    __tablename__ = "estadistica_categoria_grupo"
    id_estadistica_grupo = Column(Integer, primary_key=True, index=True)
    promedio_tiempo = Column(Float)
    promedio_dificultad = Column(Float)
    total_tareas = Column(Integer)
    id_grupo = Column(Integer, ForeignKey("grupos.id_grupo", ondelete="CASCADE"))
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))


class SesionesCronometro(base):
    __tablename__ = "sesiones_cronometro"
    id_sesion = Column(Integer, primary_key=True, index=True)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime)
    duracion = Column(Float)
    id_tarea = Column(
        Integer, ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=False)