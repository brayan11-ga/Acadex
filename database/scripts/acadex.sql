-- ============================================================
-- AC A D E X
-- ============================================================

-- ============================================================
-- 1. USUARIOS
-- ============================================================

CREATE TABLE usuarios (
    id_usuario INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    correo_electronico VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(60) NOT NULL,
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE,
    es_admin BOOLEAN NOT NULL DEFAULT FALSE
);


-- ============================================================
-- 2. CATEGORÍAS
-- ============================================================

CREATE TABLE categorias (
    id_categoria INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_categoria VARCHAR(50) NOT NULL UNIQUE
);


-- ============================================================
-- 3. GRUPOS
-- ============================================================

CREATE TABLE grupos (
    id_grupo INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_grupo VARCHAR(50) NOT NULL,
    descripcion TEXT,
    codigo_acceso VARCHAR(20) NOT NULL UNIQUE,
    fecha_creacion DATE NOT NULL DEFAULT CURRENT_DATE
);


-- ============================================================
-- 4. INTEGRANTES
-- ============================================================

CREATE TABLE integrantes (
    id_integrante INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rol VARCHAR(50) NOT NULL,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    id_usuario INTEGER NOT NULL,
    id_grupo INTEGER NOT NULL,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_grupo)
        REFERENCES grupos(id_grupo)
        ON DELETE CASCADE,

    CONSTRAINT chk_rol_integrante
        CHECK (rol IN ('lider', 'miembro')),

    CONSTRAINT uq_usuario_grupo
        UNIQUE (id_usuario, id_grupo)
);


-- ============================================================
-- 5. TAREAS
-- ============================================================

CREATE TABLE tareas (
    id_tarea INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,

    descripcion TEXT,

    fecha_entrega TIMESTAMP NOT NULL,

    estado VARCHAR(50) NOT NULL DEFAULT 'pendiente',

    dificultad_estimada INTEGER NOT NULL,

    tiempo_estimado INTEGER NOT NULL,

    prioridad INTEGER,

    tiempo_acumulado REAL NOT NULL DEFAULT 0,

    cronometro_activo BOOLEAN NOT NULL DEFAULT FALSE,

    ultima_pausa TIMESTAMP,

    id_usuario INTEGER,

    id_grupo INTEGER,

    id_categoria INTEGER NOT NULL,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),

    FOREIGN KEY (id_grupo)
        REFERENCES grupos(id_grupo)
        ON DELETE CASCADE,

    FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria),

    CONSTRAINT chk_dificultad_estimada
        CHECK (dificultad_estimada BETWEEN 1 AND 5),

    CONSTRAINT chk_tiempo_estimado
        CHECK (tiempo_estimado > 0),

    CONSTRAINT chk_prioridad
        CHECK (prioridad IS NULL OR prioridad > 0),

    CONSTRAINT chk_tarea_owner
        CHECK (
            (id_usuario IS NOT NULL AND id_grupo IS NULL)
            OR
            (id_usuario IS NULL AND id_grupo IS NOT NULL)
        )
);


-- ============================================================
-- 6. ASIGNACIÓN DE TAREAS
-- ============================================================

CREATE TABLE asignacion_tareas (
    id_asignacion INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    fecha_asignacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    id_tarea INTEGER NOT NULL,

    id_integrante INTEGER NOT NULL,

    FOREIGN KEY (id_tarea)
        REFERENCES tareas(id_tarea)
        ON DELETE CASCADE,

    FOREIGN KEY (id_integrante)
        REFERENCES integrantes(id_integrante)
        ON DELETE CASCADE,

    CONSTRAINT uq_tarea_integrante
        UNIQUE (id_tarea, id_integrante)
);


-- ============================================================
-- 7. PERFILES
-- ============================================================

CREATE TABLE perfiles (
    id_perfil INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    nombre_usuario VARCHAR(50) NOT NULL,

    telefono VARCHAR(20),

    foto_perfil VARCHAR(255),

    descripcion TEXT,

    notif_activas BOOLEAN NOT NULL DEFAULT TRUE,

    limite_cronometro INTEGER,

    id_usuario INTEGER NOT NULL UNIQUE,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT chk_limite_cronometro
        CHECK (
            limite_cronometro IS NULL
            OR limite_cronometro > 0
        )
);


-- ============================================================
-- 8. TOKENS TEMPORALES
-- ============================================================

CREATE TABLE tokens_temporales (
    id_token INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tipo_token VARCHAR(50) NOT NULL,

    valor_token VARCHAR(50) NOT NULL UNIQUE,

    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    fecha_expiracion TIMESTAMP NOT NULL,

    usado BOOLEAN NOT NULL DEFAULT FALSE,

    id_usuario INTEGER,

    id_grupo INTEGER,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,

    FOREIGN KEY (id_grupo)
        REFERENCES grupos(id_grupo)
        ON DELETE CASCADE,

    CONSTRAINT chk_fecha_token
        CHECK (fecha_expiracion > fecha_creacion)
);


-- ============================================================
-- 9. SESIONES DEL CRONÓMETRO
-- ============================================================

CREATE TABLE sesiones_cronometro (
    id_sesion INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    fecha_inicio TIMESTAMP NOT NULL,

    fecha_fin TIMESTAMP,

    duracion REAL,

    id_tarea INTEGER NOT NULL,

    id_usuario INTEGER NOT NULL,

    FOREIGN KEY (id_tarea)
        REFERENCES tareas(id_tarea)
        ON DELETE CASCADE,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT chk_duracion_sesion
        CHECK (duracion IS NULL OR duracion >= 0),

    CONSTRAINT chk_fechas_sesion
        CHECK (
            fecha_fin IS NULL
            OR fecha_fin >= fecha_inicio
        )
);


-- ============================================================
-- 10. HISTORIAL DE TAREAS
-- ============================================================

CREATE TABLE historial_tareas (
    id_historial INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    fechahora_fin TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    tiempo_real REAL,

    dificultad_real INTEGER,

    id_usuario INTEGER NOT NULL,

    id_tarea INTEGER NOT NULL,

    id_grupo INTEGER,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,

    FOREIGN KEY (id_tarea)
        REFERENCES tareas(id_tarea)
        ON DELETE CASCADE,

    FOREIGN KEY (id_grupo)
        REFERENCES grupos(id_grupo)
        ON DELETE CASCADE,

    CONSTRAINT chk_dificultad_real
        CHECK (
            dificultad_real IS NULL
            OR dificultad_real BETWEEN 1 AND 5
        ),

    CONSTRAINT chk_tiempo_real
        CHECK (
            tiempo_real IS NULL
            OR tiempo_real >= 0
        )
);


-- ============================================================
-- 11. ARCHIVOS
-- ============================================================

CREATE TABLE archivos (
    id_archivo INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL,

    tamano BIGINT,

    tipo VARCHAR(10) NOT NULL,

    fecha_adjuncion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    ruta VARCHAR(255) NOT NULL,

    id_tarea INTEGER NOT NULL,

    FOREIGN KEY (id_tarea)
        REFERENCES tareas(id_tarea)
        ON DELETE CASCADE,

    CONSTRAINT chk_tamano_archivo
        CHECK (
            tamano IS NULL
            OR tamano >= 0
        ),

    CONSTRAINT chk_tipo_archivo
        CHECK (
            tipo IN ('PDF', 'DOCX', 'JPG', 'PNG')
        )
);


-- ============================================================
-- 12. NOTIFICACIONES
-- ============================================================

CREATE TABLE notificaciones (
    id_notificacion INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    titulo VARCHAR(50) NOT NULL,

    detalles VARCHAR(100),

    fecha_envio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    estado BOOLEAN NOT NULL DEFAULT FALSE,

    tipo VARCHAR(50) NOT NULL,

    id_usuario INTEGER NOT NULL,

    id_tarea INTEGER,

    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,

    FOREIGN KEY (id_tarea)
        REFERENCES tareas(id_tarea)
        ON DELETE CASCADE
);


-- ============================================================
-- 13. ESTADÍSTICAS POR CATEGORÍA Y USUARIO
-- ============================================================

CREATE TABLE estadistica_categoria (
    id_estadistica_categoria INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    promedio_tiempo REAL,

    promedio_dificultad REAL,

    total_tareas INTEGER,

    id_perfil INTEGER NOT NULL,

    id_categoria INTEGER NOT NULL,

    FOREIGN KEY (id_perfil)
        REFERENCES perfiles(id_perfil)
        ON DELETE CASCADE,

    FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
        ON DELETE CASCADE,

    CONSTRAINT chk_total_tareas
        CHECK (
            total_tareas IS NULL
            OR total_tareas >= 0
        ),

    CONSTRAINT chk_promedio_dificultad
        CHECK (
            promedio_dificultad IS NULL
            OR promedio_dificultad BETWEEN 1 AND 5
        )
);


-- ============================================================
-- 14. ESTADÍSTICAS POR CATEGORÍA Y GRUPO
-- ============================================================

CREATE TABLE estadistica_categoria_grupo (
    id_estadistica_grupo INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    promedio_tiempo REAL,

    promedio_dificultad REAL,

    total_tareas INTEGER,

    id_grupo INTEGER NOT NULL,

    id_categoria INTEGER NOT NULL,

    FOREIGN KEY (id_grupo)
        REFERENCES grupos(id_grupo)
        ON DELETE CASCADE,

    FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
        ON DELETE CASCADE,

    CONSTRAINT chk_total_tareas_grupo
        CHECK (
            total_tareas IS NULL
            OR total_tareas >= 0
        ),

    CONSTRAINT chk_promedio_dificultad_grupo
        CHECK (
            promedio_dificultad IS NULL
            OR promedio_dificultad BETWEEN 1 AND 5
        )
);


-- ============================================================
-- 15. ÍNDICES
-- ============================================================

CREATE INDEX idx_tareas_nombre
    ON tareas(nombre);

CREATE INDEX idx_tareas_fecha_entrega
    ON tareas(fecha_entrega);

CREATE INDEX idx_tareas_usuario
    ON tareas(id_usuario);

CREATE INDEX idx_tareas_grupo
    ON tareas(id_grupo);

CREATE INDEX idx_tareas_categoria
    ON tareas(id_categoria);

CREATE INDEX idx_integrantes_usuario
    ON integrantes(id_usuario);

CREATE INDEX idx_integrantes_grupo
    ON integrantes(id_grupo);

CREATE INDEX idx_asignacion_tarea
    ON asignacion_tareas(id_tarea);

CREATE INDEX idx_asignacion_integrante
    ON asignacion_tareas(id_integrante);

CREATE INDEX idx_sesiones_tarea
    ON sesiones_cronometro(id_tarea);

CREATE INDEX idx_sesiones_usuario
    ON sesiones_cronometro(id_usuario);

CREATE INDEX idx_historial_tarea
    ON historial_tareas(id_tarea);

CREATE INDEX idx_historial_usuario
    ON historial_tareas(id_usuario);

CREATE INDEX idx_archivos_tarea
    ON archivos(id_tarea);

CREATE INDEX idx_notificaciones_usuario
    ON notificaciones(id_usuario);

CREATE INDEX idx_notificaciones_tarea
    ON notificaciones(id_tarea);