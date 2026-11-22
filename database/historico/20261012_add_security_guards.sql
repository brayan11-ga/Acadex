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
