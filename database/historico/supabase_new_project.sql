-- HISTORICO: snapshot del antiguo bootstrap manual de Supabase.
-- No ejecutar como flujo vigente: el esquema se versiona en backend/alembic/.
-- Este archivo tambien habilita RLS; esa configuracion se reconciliara en una
-- fase de seguridad separada. Se conserva sin cambios SQL para comparacion.

-- ===== Esquema base y categorias =====

--
-- PostgreSQL database dump
--


-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: archivos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.archivos (
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


--
-- Name: archivos_id_archivo_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.archivos ALTER COLUMN id_archivo ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.archivos_id_archivo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: asignacion_tareas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.asignacion_tareas (
    id_asignacion integer NOT NULL,
    fecha_asignacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_tarea integer NOT NULL,
    id_integrante integer NOT NULL
);


--
-- Name: asignacion_tareas_id_asignacion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.asignacion_tareas ALTER COLUMN id_asignacion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.asignacion_tareas_id_asignacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: categorias; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categorias (
    id_categoria integer NOT NULL,
    nombre_categoria character varying(50) NOT NULL
);


--
-- Name: categorias_id_categoria_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.categorias ALTER COLUMN id_categoria ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.categorias_id_categoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: estadistica_categoria; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: estadistica_categoria_grupo; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: estadistica_categoria_grupo_id_estadistica_grupo_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.estadistica_categoria_grupo ALTER COLUMN id_estadistica_grupo ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.estadistica_categoria_grupo_id_estadistica_grupo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: estadistica_categoria_id_estadistica_categoria_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.estadistica_categoria ALTER COLUMN id_estadistica_categoria ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.estadistica_categoria_id_estadistica_categoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: grupos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.grupos (
    id_grupo integer NOT NULL,
    nombre_grupo character varying(50) NOT NULL,
    descripcion text,
    codigo_acceso character varying(20) NOT NULL,
    fecha_creacion date DEFAULT CURRENT_DATE NOT NULL
);


--
-- Name: grupos_id_grupo_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.grupos ALTER COLUMN id_grupo ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.grupos_id_grupo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: historial_tareas; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: historial_tareas_id_historial_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.historial_tareas ALTER COLUMN id_historial ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.historial_tareas_id_historial_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: integrantes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.integrantes (
    id_integrante integer NOT NULL,
    rol character varying(50) NOT NULL,
    fecha_ingreso date DEFAULT CURRENT_DATE NOT NULL,
    id_usuario integer NOT NULL,
    id_grupo integer NOT NULL,
    CONSTRAINT chk_rol_integrante CHECK (((rol)::text = ANY ((ARRAY['lider'::character varying, 'miembro'::character varying])::text[])))
);


--
-- Name: integrantes_id_integrante_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.integrantes ALTER COLUMN id_integrante ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.integrantes_id_integrante_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: notificaciones; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: notificaciones_id_notificacion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.notificaciones ALTER COLUMN id_notificacion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.notificaciones_id_notificacion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: perfiles; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: perfiles_id_perfil_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.perfiles ALTER COLUMN id_perfil ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.perfiles_id_perfil_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: sesiones_cronometro; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: sesiones_cronometro_id_sesion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.sesiones_cronometro ALTER COLUMN id_sesion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.sesiones_cronometro_id_sesion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tareas; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: tareas_id_tarea_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.tareas ALTER COLUMN id_tarea ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tareas_id_tarea_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tokens_temporales; Type: TABLE; Schema: public; Owner: -
--

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


--
-- Name: tokens_temporales_id_token_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.tokens_temporales ALTER COLUMN id_token ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tokens_temporales_id_token_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id_usuario integer NOT NULL,
    correo_electronico character varying(100) NOT NULL,
    contrasena character varying(60) NOT NULL,
    fecha_registro date DEFAULT CURRENT_DATE NOT NULL,
    es_admin boolean DEFAULT false NOT NULL
);


--
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.usuarios ALTER COLUMN id_usuario ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.usuarios_id_usuario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: archivos archivos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archivos
    ADD CONSTRAINT archivos_pkey PRIMARY KEY (id_archivo);


--
-- Name: asignacion_tareas asignacion_tareas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignacion_tareas
    ADD CONSTRAINT asignacion_tareas_pkey PRIMARY KEY (id_asignacion);


--
-- Name: categorias categorias_nombre_categoria_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_nombre_categoria_key UNIQUE (nombre_categoria);


--
-- Name: categorias categorias_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_pkey PRIMARY KEY (id_categoria);


--
-- Name: estadistica_categoria_grupo estadistica_categoria_grupo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estadistica_categoria_grupo
    ADD CONSTRAINT estadistica_categoria_grupo_pkey PRIMARY KEY (id_estadistica_grupo);


--
-- Name: estadistica_categoria estadistica_categoria_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estadistica_categoria
    ADD CONSTRAINT estadistica_categoria_pkey PRIMARY KEY (id_estadistica_categoria);


--
-- Name: grupos grupos_codigo_acceso_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grupos
    ADD CONSTRAINT grupos_codigo_acceso_key UNIQUE (codigo_acceso);


--
-- Name: grupos grupos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.grupos
    ADD CONSTRAINT grupos_pkey PRIMARY KEY (id_grupo);


--
-- Name: historial_tareas historial_tareas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historial_tareas
    ADD CONSTRAINT historial_tareas_pkey PRIMARY KEY (id_historial);


--
-- Name: integrantes integrantes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integrantes
    ADD CONSTRAINT integrantes_pkey PRIMARY KEY (id_integrante);


--
-- Name: notificaciones notificaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_pkey PRIMARY KEY (id_notificacion);


--
-- Name: perfiles perfiles_id_usuario_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.perfiles
    ADD CONSTRAINT perfiles_id_usuario_key UNIQUE (id_usuario);


--
-- Name: perfiles perfiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.perfiles
    ADD CONSTRAINT perfiles_pkey PRIMARY KEY (id_perfil);


--
-- Name: sesiones_cronometro sesiones_cronometro_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones_cronometro
    ADD CONSTRAINT sesiones_cronometro_pkey PRIMARY KEY (id_sesion);


--
-- Name: tareas tareas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tareas
    ADD CONSTRAINT tareas_pkey PRIMARY KEY (id_tarea);


--
-- Name: tokens_temporales tokens_temporales_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tokens_temporales
    ADD CONSTRAINT tokens_temporales_pkey PRIMARY KEY (id_token);


--
-- Name: tokens_temporales tokens_temporales_valor_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tokens_temporales
    ADD CONSTRAINT tokens_temporales_valor_token_key UNIQUE (valor_token);


--
-- Name: asignacion_tareas uq_tarea_integrante; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignacion_tareas
    ADD CONSTRAINT uq_tarea_integrante UNIQUE (id_tarea, id_integrante);


--
-- Name: integrantes uq_usuario_grupo; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integrantes
    ADD CONSTRAINT uq_usuario_grupo UNIQUE (id_usuario, id_grupo);


--
-- Name: usuarios usuarios_correo_electronico_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_correo_electronico_key UNIQUE (correo_electronico);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- Name: idx_archivos_tarea; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_archivos_tarea ON public.archivos USING btree (id_tarea);


--
-- Name: idx_asignacion_integrante; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asignacion_integrante ON public.asignacion_tareas USING btree (id_integrante);


--
-- Name: idx_asignacion_tarea; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_asignacion_tarea ON public.asignacion_tareas USING btree (id_tarea);


--
-- Name: idx_historial_tarea; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_historial_tarea ON public.historial_tareas USING btree (id_tarea);


--
-- Name: idx_historial_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_historial_usuario ON public.historial_tareas USING btree (id_usuario);


--
-- Name: idx_integrantes_grupo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_integrantes_grupo ON public.integrantes USING btree (id_grupo);


--
-- Name: idx_integrantes_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_integrantes_usuario ON public.integrantes USING btree (id_usuario);


--
-- Name: idx_notificaciones_tarea; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_notificaciones_tarea ON public.notificaciones USING btree (id_tarea);


--
-- Name: idx_notificaciones_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_notificaciones_usuario ON public.notificaciones USING btree (id_usuario);


--
-- Name: idx_sesiones_tarea; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sesiones_tarea ON public.sesiones_cronometro USING btree (id_tarea);


--
-- Name: idx_sesiones_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sesiones_usuario ON public.sesiones_cronometro USING btree (id_usuario);


--
-- Name: idx_tareas_categoria; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tareas_categoria ON public.tareas USING btree (id_categoria);


--
-- Name: idx_tareas_fecha_entrega; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tareas_fecha_entrega ON public.tareas USING btree (fecha_entrega);


--
-- Name: idx_tareas_grupo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tareas_grupo ON public.tareas USING btree (id_grupo);


--
-- Name: idx_tareas_nombre; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tareas_nombre ON public.tareas USING btree (nombre);


--
-- Name: idx_tareas_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tareas_usuario ON public.tareas USING btree (id_usuario);


--
-- Name: archivos archivos_id_tarea_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.archivos
    ADD CONSTRAINT archivos_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;


--
-- Name: asignacion_tareas asignacion_tareas_id_integrante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignacion_tareas
    ADD CONSTRAINT asignacion_tareas_id_integrante_fkey FOREIGN KEY (id_integrante) REFERENCES public.integrantes(id_integrante) ON DELETE CASCADE;


--
-- Name: asignacion_tareas asignacion_tareas_id_tarea_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.asignacion_tareas
    ADD CONSTRAINT asignacion_tareas_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;


--
-- Name: estadistica_categoria_grupo estadistica_categoria_grupo_id_categoria_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estadistica_categoria_grupo
    ADD CONSTRAINT estadistica_categoria_grupo_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categorias(id_categoria) ON DELETE CASCADE;


--
-- Name: estadistica_categoria_grupo estadistica_categoria_grupo_id_grupo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estadistica_categoria_grupo
    ADD CONSTRAINT estadistica_categoria_grupo_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;


--
-- Name: estadistica_categoria estadistica_categoria_id_categoria_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estadistica_categoria
    ADD CONSTRAINT estadistica_categoria_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categorias(id_categoria) ON DELETE CASCADE;


--
-- Name: estadistica_categoria estadistica_categoria_id_perfil_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estadistica_categoria
    ADD CONSTRAINT estadistica_categoria_id_perfil_fkey FOREIGN KEY (id_perfil) REFERENCES public.perfiles(id_perfil) ON DELETE CASCADE;


--
-- Name: historial_tareas historial_tareas_id_grupo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historial_tareas
    ADD CONSTRAINT historial_tareas_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;


--
-- Name: historial_tareas historial_tareas_id_tarea_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historial_tareas
    ADD CONSTRAINT historial_tareas_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;


--
-- Name: historial_tareas historial_tareas_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historial_tareas
    ADD CONSTRAINT historial_tareas_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: integrantes integrantes_id_grupo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integrantes
    ADD CONSTRAINT integrantes_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;


--
-- Name: integrantes integrantes_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integrantes
    ADD CONSTRAINT integrantes_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario);


--
-- Name: notificaciones notificaciones_id_tarea_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;


--
-- Name: notificaciones notificaciones_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: perfiles perfiles_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.perfiles
    ADD CONSTRAINT perfiles_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: sesiones_cronometro sesiones_cronometro_id_tarea_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones_cronometro
    ADD CONSTRAINT sesiones_cronometro_id_tarea_fkey FOREIGN KEY (id_tarea) REFERENCES public.tareas(id_tarea) ON DELETE CASCADE;


--
-- Name: sesiones_cronometro sesiones_cronometro_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sesiones_cronometro
    ADD CONSTRAINT sesiones_cronometro_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- Name: tareas tareas_id_categoria_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tareas
    ADD CONSTRAINT tareas_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categorias(id_categoria);


--
-- Name: tareas tareas_id_grupo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tareas
    ADD CONSTRAINT tareas_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;


--
-- Name: tareas tareas_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tareas
    ADD CONSTRAINT tareas_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario);


--
-- Name: tokens_temporales tokens_temporales_id_grupo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tokens_temporales
    ADD CONSTRAINT tokens_temporales_id_grupo_fkey FOREIGN KEY (id_grupo) REFERENCES public.grupos(id_grupo) ON DELETE CASCADE;


--
-- Name: tokens_temporales tokens_temporales_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tokens_temporales
    ADD CONSTRAINT tokens_temporales_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


-- Datos iniciales: categorías
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
ON CONFLICT (nombre_categoria) DO NOTHING;

-- Las migraciones siguientes usan nombres sin esquema.
SET search_path TO public;


-- ===== Migracion 20261011_add_archivo_uploader.sql =====

-- Añade autoría para nuevas subidas. Los registros existentes quedan con autor desconocido.
BEGIN;

ALTER TABLE archivos
    ADD COLUMN IF NOT EXISTS id_usuario_subida INTEGER NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_archivos_usuario_subida'
          AND conrelid = 'archivos'::regclass
    ) THEN
        ALTER TABLE archivos
            ADD CONSTRAINT fk_archivos_usuario_subida
            FOREIGN KEY (id_usuario_subida)
            REFERENCES usuarios (id_usuario)
            ON DELETE SET NULL;
    END IF;
END
$$;

COMMENT ON COLUMN archivos.id_usuario_subida IS
    'Usuario autenticado que subió el adjunto; NULL identifica registros históricos sin autor verificable.';

COMMIT;


-- ===== Migracion 20261011_add_registration_consents.sql =====

-- Registra versiones y fechas sin inventar consentimientos para cuentas existentes.
BEGIN;

CREATE TABLE IF NOT EXISTS consentimientos_usuario (
    id_consentimiento INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    id_usuario INTEGER NOT NULL
        REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    tipo_consentimiento VARCHAR(40) NOT NULL,
    version_politica VARCHAR(30) NOT NULL,
    fecha_aceptacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_consentimientos_usuario_tipo
        CHECK (tipo_consentimiento IN ('tratamiento_datos', 'aviso_almacenamiento')),
    CONSTRAINT uq_consentimientos_usuario_version
        UNIQUE (id_usuario, tipo_consentimiento, version_politica)
);

COMMENT ON TABLE consentimientos_usuario IS
    'Evidencia versionada de autorización de tratamiento de datos y lectura del aviso de almacenamiento local.';

COMMIT;


-- ===== Migracion 20261012_add_gemini_usage_limits.sql =====

-- Contadores mínimos para limitar las llamadas a Gemini por usuario y por día.
-- No almacena contenido de documentos ni respuestas generadas.
BEGIN;

CREATE TABLE IF NOT EXISTS uso_analisis_ia (
    fecha_utc DATE NOT NULL,
    alcance VARCHAR(10) NOT NULL,
    identificador_alcance VARCHAR(64) NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT pk_uso_analisis_ia
        PRIMARY KEY (fecha_utc, alcance, identificador_alcance),
    CONSTRAINT ck_uso_analisis_ia_cantidad
        CHECK (cantidad >= 0),
    CONSTRAINT ck_uso_analisis_ia_alcance
        CHECK (
            (alcance = 'usuario' AND identificador_alcance <> '')
            OR (alcance = 'global' AND identificador_alcance = 'global')
        )
);

COMMIT;


-- ===== Migracion 20261012_add_gemini_quota_lockout.sql =====

-- Bloqueo persistente del análisis cuando Google informa que se agotó la cuota RPD.
-- No almacena documentos, respuestas ni mensajes del proveedor.
BEGIN;

CREATE TABLE IF NOT EXISTS bloqueo_cuota_gemini (
    id VARCHAR(32) PRIMARY KEY,
    bloqueado_hasta TIMESTAMPTZ NOT NULL,
    CONSTRAINT ck_bloqueo_cuota_gemini_id
        CHECK (id = 'proyecto')
);

COMMIT;


-- ===== Migracion 20261012_add_security_guards.sql =====

-- Límites de acceso compartidos, desbloqueo temporal y unicidad de cronómetro.
-- No elimina ni modifica filas existentes. Si hay sesiones activas duplicadas,
-- aborta antes de crear el índice para que un operador las revise manualmente.
BEGIN;

ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS intentos_fallidos INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS bloqueado BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS bloqueado_hasta TIMESTAMP WITHOUT TIME ZONE;

CREATE TABLE IF NOT EXISTS limites_solicitud (
    alcance VARCHAR(40) NOT NULL,
    clave_hash VARCHAR(64) NOT NULL,
    inicio_ventana TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT pk_limites_solicitud PRIMARY KEY (alcance, clave_hash),
    CONSTRAINT ck_limites_solicitud_cantidad CHECK (cantidad >= 0)
);

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM sesiones_cronometro
        WHERE fecha_fin IS NULL
        GROUP BY id_tarea
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION
            'Hay tareas con varias sesiones activas. Revise esas filas antes de aplicar 20261012_add_security_guards.sql.';
    END IF;
END
$$;

CREATE UNIQUE INDEX IF NOT EXISTS uq_sesiones_tarea_activa
    ON sesiones_cronometro (id_tarea)
    WHERE fecha_fin IS NULL;

COMMIT;


-- Denegar acceso por Data API a tablas ACADEX sin politicas explicitas.

ALTER TABLE public.archivos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.asignacion_tareas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.categorias ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.estadistica_categoria ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.estadistica_categoria_grupo ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.grupos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historial_tareas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.integrantes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notificaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.perfiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sesiones_cronometro ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tareas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tokens_temporales ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consentimientos_usuario ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uso_analisis_ia ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bloqueo_cuota_gemini ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.limites_solicitud ENABLE ROW LEVEL SECURITY;

-- ===== Verificacion: las 11 columnas deben ser true =====

SELECT
    to_regclass('public.consentimientos_usuario') IS NOT NULL AS tabla_consentimientos,
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'archivos'
          AND column_name = 'id_usuario_subida'
          AND data_type = 'integer'
          AND is_nullable = 'YES'
    ) AS autor_archivo_nullable_integer,
    EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = to_regclass('public.consentimientos_usuario')
          AND conname = 'uq_consentimientos_usuario_version'
          AND contype = 'u'
    ) AS unicidad_consentimiento,
    EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = to_regclass('public.consentimientos_usuario')
          AND conname = 'chk_consentimientos_usuario_tipo'
          AND contype = 'c'
    ) AS tipos_consentimiento_validos,
    EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = to_regclass('public.consentimientos_usuario')
          AND confrelid = to_regclass('public.usuarios')
          AND conname = 'consentimientos_usuario_id_usuario_fkey'
          AND contype = 'f'
          AND confdeltype = 'c'
    ) AS usuario_de_consentimiento_fk_cascade,
    EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = to_regclass('public.archivos')
          AND conname = 'fk_archivos_usuario_subida'
          AND contype = 'f'
          AND confdeltype = 'n'
    ) AS autor_archivo_fk_set_null,
    to_regclass('public.uso_analisis_ia') IS NOT NULL AS tabla_limites_ia,
    to_regclass('public.bloqueo_cuota_gemini') IS NOT NULL AS tabla_bloqueo_cuota_gemini,
    to_regclass('public.limites_solicitud') IS NOT NULL AS tabla_limites_solicitud,
    EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'usuarios'
          AND column_name = 'bloqueado_hasta'
          AND data_type = 'timestamp without time zone'
    ) AS vencimiento_bloqueo_cuenta,
    EXISTS (
        SELECT 1
        FROM pg_index
        WHERE indexrelid = to_regclass('public.uq_sesiones_tarea_activa')
          AND indisunique
          AND pg_get_expr(indpred, indrelid) = '(fecha_fin IS NULL)'
    ) AS unicidad_sesion_activa_por_tarea;

