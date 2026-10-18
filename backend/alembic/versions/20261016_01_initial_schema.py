"""Esquema base validado: snapshot autocontenido de database/init.sql.

La revisión conserva las definiciones, índices, restricciones, identidades y
nueve categorías de la inicialización PostgreSQL validada en Fase 1.1. Se
embebe aquí para que el despliegue del backend no dependa de montar database/.
"""

from alembic import op


revision = "20261016_01"
down_revision = None
branch_labels = None
depends_on = None


_BASE_SCHEMA_SQL = r'''CREATE TABLE public.archivos (
    id_archivo integer NOT NULL,
    nombre character varying(100) NOT NULL,
    tamano bigint,
    tipo character varying(10) NOT NULL,
    fecha_adjuncion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ruta character varying(255) NOT NULL,
    id_tarea integer NOT NULL,
    CONSTRAINT chk_tamano_archivo CHECK (((tamano IS NULL) OR (tamano >= 0))),
    CONSTRAINT chk_tipo_archivo CHECK (((tipo)::text = ANY ((ARRAY['PDF'::character varying, 'DOCX'::character varying, 'JPG'::character varying, 'PNG'::character varying])::text[])))
);



ALTER TABLE public.archivos ALTER COLUMN id_archivo ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.archivos_id_archivo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.asignacion_tareas (
    id_asignacion integer NOT NULL,
    fecha_asignacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_tarea integer NOT NULL,
    id_integrante integer NOT NULL
);



ALTER TABLE public.asignacion_tareas ALTER COLUMN id_asignacion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.asignacion_tareas_id_asignacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.categorias (
    id_categoria integer NOT NULL,
    nombre_categoria character varying(50) NOT NULL
);



ALTER TABLE public.categorias ALTER COLUMN id_categoria ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.categorias_id_categoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.estadistica_categoria (
    id_estadistica_categoria integer NOT NULL,
    promedio_tiempo real,
    promedio_dificultad real,
    total_tareas integer,
    id_perfil integer NOT NULL,
    id_categoria integer NOT NULL,
    CONSTRAINT chk_promedio_dificultad CHECK (((promedio_dificultad IS NULL) OR ((promedio_dificultad >= (1)::double precision) AND (promedio_dificultad <= (5)::double precision)))),
    CONSTRAINT chk_total_tareas CHECK (((total_tareas IS NULL) OR (total_tareas >= 0)))
);



CREATE TABLE public.estadistica_categoria_grupo (
    id_estadistica_grupo integer NOT NULL,
    promedio_tiempo real,
    promedio_dificultad real,
    total_tareas integer,
    id_grupo integer NOT NULL,
    id_categoria integer NOT NULL,
    CONSTRAINT chk_promedio_dificultad_grupo CHECK (((promedio_dificultad IS NULL) OR ((promedio_dificultad >= (1)::double precision) AND (promedio_dificultad <= (5)::double precision)))),
    CONSTRAINT chk_total_tareas_grupo CHECK (((total_tareas IS NULL) OR (total_tareas >= 0)))
);



ALTER TABLE public.estadistica_categoria_grupo ALTER COLUMN id_estadistica_grupo ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.estadistica_categoria_grupo_id_estadistica_grupo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



ALTER TABLE public.estadistica_categoria ALTER COLUMN id_estadistica_categoria ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.estadistica_categoria_id_estadistica_categoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.grupos (
    id_grupo integer NOT NULL,
    nombre_grupo character varying(50) NOT NULL,
    descripcion text,
    codigo_acceso character varying(20) NOT NULL,
    fecha_creacion date DEFAULT CURRENT_DATE NOT NULL
);



ALTER TABLE public.grupos ALTER COLUMN id_grupo ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.grupos_id_grupo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.historial_tareas (
    id_historial integer NOT NULL,
    fechahora_fin timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    tiempo_real real,
    dificultad_real integer,
    id_usuario integer NOT NULL,
    id_tarea integer NOT NULL,
    id_grupo integer,
    CONSTRAINT chk_dificultad_real CHECK (((dificultad_real IS NULL) OR ((dificultad_real >= 1) AND (dificultad_real <= 5)))),
    CONSTRAINT chk_tiempo_real CHECK (((tiempo_real IS NULL) OR (tiempo_real >= (0)::double precision)))
);



ALTER TABLE public.historial_tareas ALTER COLUMN id_historial ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.historial_tareas_id_historial_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.integrantes (
    id_integrante integer NOT NULL,
    rol character varying(50) NOT NULL,
    fecha_ingreso date DEFAULT CURRENT_DATE NOT NULL,
    id_usuario integer NOT NULL,
    id_grupo integer NOT NULL,
    CONSTRAINT chk_rol_integrante CHECK (((rol)::text = ANY ((ARRAY['lider'::character varying, 'miembro'::character varying])::text[])))
);



ALTER TABLE public.integrantes ALTER COLUMN id_integrante ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.integrantes_id_integrante_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.notificaciones (
    id_notificacion integer NOT NULL,
    titulo character varying(50) NOT NULL,
    detalles character varying(100),
    fecha_envio timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado boolean DEFAULT false NOT NULL,
    tipo character varying(50) NOT NULL,
    id_usuario integer NOT NULL,
    id_tarea integer
);



ALTER TABLE public.notificaciones ALTER COLUMN id_notificacion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.notificaciones_id_notificacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.perfiles (
    id_perfil integer NOT NULL,
    nombre_usuario character varying(50) NOT NULL,
    telefono character varying(20),
    foto_perfil character varying(255),
    descripcion text,
    notif_activas boolean DEFAULT true NOT NULL,
    limite_cronometro integer,
    id_usuario integer NOT NULL,
    CONSTRAINT chk_limite_cronometro CHECK (((limite_cronometro IS NULL) OR (limite_cronometro > 0)))
);



ALTER TABLE public.perfiles ALTER COLUMN id_perfil ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.perfiles_id_perfil_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.sesiones_cronometro (
    id_sesion integer NOT NULL,
    fecha_inicio timestamp without time zone NOT NULL,
    fecha_fin timestamp without time zone,
    duracion real,
    id_tarea integer NOT NULL,
    id_usuario integer NOT NULL,
    CONSTRAINT chk_duracion_sesion CHECK (((duracion IS NULL) OR (duracion >= (0)::double precision))),
    CONSTRAINT chk_fechas_sesion CHECK (((fecha_fin IS NULL) OR (fecha_fin >= fecha_inicio)))
);



ALTER TABLE public.sesiones_cronometro ALTER COLUMN id_sesion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.sesiones_cronometro_id_sesion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.tareas (
    id_tarea integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    fecha_entrega timestamp without time zone NOT NULL,
    estado character varying(50) DEFAULT 'pendiente'::character varying NOT NULL,
    dificultad_estimada integer NOT NULL,
    tiempo_estimado integer NOT NULL,
    prioridad integer,
    tiempo_acumulado real DEFAULT 0 NOT NULL,
    cronometro_activo boolean DEFAULT false NOT NULL,
    ultima_pausa timestamp without time zone,
    id_usuario integer,
    id_grupo integer,
    id_categoria integer NOT NULL,
    CONSTRAINT chk_dificultad_estimada CHECK (((dificultad_estimada >= 1) AND (dificultad_estimada <= 5))),
    CONSTRAINT chk_prioridad CHECK (((prioridad IS NULL) OR (prioridad > 0))),
    CONSTRAINT chk_tarea_owner CHECK ((((id_usuario IS NOT NULL) AND (id_grupo IS NULL)) OR ((id_usuario IS NULL) AND (id_grupo IS NOT NULL)))),
    CONSTRAINT chk_tiempo_estimado CHECK ((tiempo_estimado > 0))
);



ALTER TABLE public.tareas ALTER COLUMN id_tarea ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tareas_id_tarea_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.tokens_temporales (
    id_token integer NOT NULL,
    tipo_token character varying(50) NOT NULL,
    valor_token character varying(50) NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_expiracion timestamp without time zone NOT NULL,
    usado boolean DEFAULT false NOT NULL,
    id_usuario integer,
    id_grupo integer,
    CONSTRAINT chk_fecha_token CHECK ((fecha_expiracion > fecha_creacion))
);



ALTER TABLE public.tokens_temporales ALTER COLUMN id_token ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tokens_temporales_id_token_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE public.usuarios (
    id_usuario integer NOT NULL,
    correo_electronico character varying(100) NOT NULL,
    contrasena character varying(60) NOT NULL,
    fecha_registro date DEFAULT CURRENT_DATE NOT NULL,
    es_admin boolean DEFAULT false NOT NULL
);



ALTER TABLE public.usuarios ALTER COLUMN id_usuario ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.usuarios_id_usuario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



ALTER TABLE ONLY public.archivos
    ADD CONSTRAINT archivos_pkey PRIMARY KEY (id_archivo);



ALTER TABLE ONLY public.asignacion_tareas
    ADD CONSTRAINT asignacion_tareas_pkey PRIMARY KEY (id_asignacion);



ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_nombre_categoria_key UNIQUE (nombre_categoria);



ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_pkey PRIMARY KEY (id_categoria);



ALTER TABLE ONLY public.estadistica_categoria_grupo
    ADD CONSTRAINT estadistica_categoria_grupo_pkey PRIMARY KEY (id_estadistica_grupo);



ALTER TABLE ONLY public.estadistica_categoria
    ADD CONSTRAINT estadistica_categoria_pkey PRIMARY KEY (id_estadistica_categoria);



ALTER TABLE ONLY public.grupos
    ADD CONSTRAINT grupos_codigo_acceso_key UNIQUE (codigo_acceso);



ALTER TABLE ONLY public.grupos
    ADD CONSTRAINT grupos_pkey PRIMARY KEY (id_grupo);



ALTER TABLE ONLY public.historial_tareas
    ADD CONSTRAINT historial_tareas_pkey PRIMARY KEY (id_historial);



ALTER TABLE ONLY public.integrantes
    ADD CONSTRAINT integrantes_pkey PRIMARY KEY (id_integrante);



ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_pkey PRIMARY KEY (id_notificacion);



ALTER TABLE ONLY public.perfiles
    ADD CONSTRAINT perfiles_id_usuario_key UNIQUE (id_usuario);



ALTER TABLE ONLY public.perfiles
    ADD CONSTRAINT perfiles_pkey PRIMARY KEY (id_perfil);



ALTER TABLE ONLY public.sesiones_cronometro
    ADD CONSTRAINT sesiones_cronometro_pkey PRIMARY KEY (id_sesion);



ALTER TABLE ONLY public.tareas
    ADD CONSTRAINT tareas_pkey PRIMARY KEY (id_tarea);



ALTER TABLE ONLY public.tokens_temporales
    ADD CONSTRAINT tokens_temporales_pkey PRIMARY KEY (id_token);



ALTER TABLE ONLY public.tokens_temporales
    ADD CONSTRAINT tokens_temporales_valor_token_key UNIQUE (valor_token);



ALTER TABLE ONLY public.asignacion_tareas
    ADD CONSTRAINT uq_tarea_integrante UNIQUE (id_tarea, id_integrante);



ALTER TABLE ONLY public.integrantes
    ADD CONSTRAINT uq_usuario_grupo UNIQUE (id_usuario, id_grupo);



ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_correo_electronico_key UNIQUE (correo_electronico);



ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);



CREATE INDEX idx_archivos_tarea ON public.archivos USING btree (id_tarea);



CREATE INDEX idx_asignacion_integrante ON public.asignacion_tareas USING btree (id_integrante);



CREATE INDEX idx_asignacion_tarea ON public.asignacion_tareas USING btree (id_tarea);



CREATE INDEX idx_historial_tarea ON public.historial_tareas USING btree (id_tarea);



CREATE INDEX idx_historial_usuario ON public.historial_tareas USING btree (id_usuario);



CREATE INDEX idx_integrantes_grupo ON public.integrantes USING btree (id_grupo);



CREATE INDEX idx_integrantes_usuario ON public.integrantes USING btree (id_usuario);



CREATE INDEX idx_notificaciones_tarea ON public.notificaciones USING btree (id_tarea);



CREATE INDEX idx_notificaciones_usuario ON public.notificaciones USING btree (id_usuario);



CREATE INDEX idx_sesiones_tarea ON public.sesiones_cronometro USING btree (id_tarea);



CREATE INDEX idx_sesiones_usuario ON public.sesiones_cronometro USING btree (id_usuario);



CREATE INDEX idx_tareas_categoria ON public.tareas USING btree (id_categoria);



CREATE INDEX idx_tareas_fecha_entrega ON public.tareas USING btree (fecha_entrega);



CREATE INDEX idx_tareas_grupo ON public.tareas USING btree (id_grupo);



CREATE INDEX idx_tareas_nombre ON public.tareas USING btree (nombre);



CREATE INDEX idx_tareas_usuario ON public.tareas USING btree (id_usuario);



ALTER TABLE ONLY public.archivos
    ADD CONSTRAINT archivos_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;



ALTER TABLE ONLY public.asignacion_tareas
    ADD CONSTRAINT asignacion_tareas_id_integrante_fkey FOREIGN KEY (id_integrante) REFERENCES public.integrantes(id_integrante) ON DELETE CASCADE;



ALTER TABLE ONLY public.asignacion_tareas
    ADD CONSTRAINT asignacion_tareas_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;



ALTER TABLE ONLY public.estadistica_categoria_grupo
    ADD CONSTRAINT estadistica_categoria_grupo_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categorias(id_categoria) ON DELETE CASCADE;



ALTER TABLE ONLY public.estadistica_categoria_grupo
    ADD CONSTRAINT estadistica_categoria_grupo_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;



ALTER TABLE ONLY public.estadistica_categoria
    ADD CONSTRAINT estadistica_categoria_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categorias(id_categoria) ON DELETE CASCADE;



ALTER TABLE ONLY public.estadistica_categoria
    ADD CONSTRAINT estadistica_categoria_id_perfil_fkey FOREIGN KEY (id_perfil) REFERENCES public.perfiles(id_perfil) ON DELETE CASCADE;



ALTER TABLE ONLY public.historial_tareas
    ADD CONSTRAINT historial_tareas_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;



ALTER TABLE ONLY public.historial_tareas
    ADD CONSTRAINT historial_tareas_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;



ALTER TABLE ONLY public.historial_tareas
    ADD CONSTRAINT historial_tareas_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;



ALTER TABLE ONLY public.integrantes
    ADD CONSTRAINT integrantes_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;



ALTER TABLE ONLY public.integrantes
    ADD CONSTRAINT integrantes_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario);



ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;



ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;



ALTER TABLE ONLY public.perfiles
    ADD CONSTRAINT perfiles_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;



ALTER TABLE ONLY public.sesiones_cronometro
    ADD CONSTRAINT sesiones_cronometro_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;



ALTER TABLE ONLY public.sesiones_cronometro
    ADD CONSTRAINT sesiones_cronometro_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;



ALTER TABLE ONLY public.tareas
    ADD CONSTRAINT tareas_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categorias(id_categoria);



ALTER TABLE ONLY public.tareas
    ADD CONSTRAINT tareas_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;



ALTER TABLE ONLY public.tareas
    ADD CONSTRAINT tareas_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario);



ALTER TABLE ONLY public.tokens_temporales
    ADD CONSTRAINT tokens_temporales_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;



ALTER TABLE ONLY public.tokens_temporales
    ADD CONSTRAINT tokens_temporales_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;




INSERT INTO public.categorias (nombre_categoria) VALUES
('Programación'),
('Base de Datos'),
('Documentación'),
('Proyecto Formativo'),
('Inglés'),
('Pruebas y QA'),
('Investigación'),
('Diseño UX/UI'),
('Matemáticas')
ON CONFLICT (nombre_categoria) DO NOTHING;'''


def upgrade() -> None:
    # init.sql es un dump PostgreSQL sin bloques PL/pgSQL; cada instrucción se
    # envía por separado para mantener errores localizables y la transacción
    # Alembic completa.
    for statement in _BASE_SCHEMA_SQL.split(";"):
        sql = statement.strip()
        if sql:
            op.execute(sql)


def downgrade() -> None:
    raise RuntimeError(
        "La revisión base crea todas las tablas iniciales y sus datos de "
        "referencia. No hay downgrade automático porque podría destruir datos."
    )