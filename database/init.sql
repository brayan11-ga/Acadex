-- init.sql – creación de tablas principales para Acadex
-- ------------------------------------------------------------
-- Usuarios y roles
CREATE TABLE IF NOT EXISTS public.usuario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    hash_contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('admin','lider','colaborador')),
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Categorías de tareas
CREATE TABLE IF NOT EXISTS public.categoria (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tareas
CREATE TABLE IF NOT EXISTS public.tarea (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha_entrega DATE NOT NULL,
    prioridad INTEGER NOT NULL CHECK (prioridad BETWEEN 1 AND 5),
    dificultad_estimada INTEGER,
    tiempo_estimado INTEGER,
    id_categoria INTEGER REFERENCES public.categoria(id) ON DELETE SET NULL,
    id_usuario INTEGER REFERENCES public.usuario(id) ON DELETE CASCADE,
    id_grupo INTEGER,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    creada_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    actualizada_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Estadísticas por categoría (ejemplo de tabla de reporte)
CREATE TABLE IF NOT EXISTS public.estadistica_categoria (
    id SERIAL PRIMARY KEY,
    id_categoria INTEGER REFERENCES public.categoria(id) ON DELETE CASCADE,
    total_tareas INTEGER NOT NULL DEFAULT 0,
    tareas_completadas INTEGER NOT NULL DEFAULT 0,
    promedio_tiempo_estimado NUMERIC(5,2) DEFAULT 0
);

-- Índices de búsqueda frecuente
CREATE INDEX IF NOT EXISTS idx_tarea_usuario ON public.tarea(id_usuario);
CREATE INDEX IF NOT EXISTS idx_tarea_categoria ON public.tarea(id_categoria);

-- Comentario: los triggers para actualizar "actualizada_en" y la tabla de estadísticas pueden añadirse después.
