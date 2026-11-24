-- Ruta: database/migrations/20261018_add_tarea_max_archivos.sql
-- Migración manual (Supabase / psql): límite de archivos por tarea.
-- Equivale a la revisión Alembic 20261018_01_add_tarea_max_archivos.py.
-- Idempotente: se puede ejecutar más de una vez sin error.
BEGIN;

ALTER TABLE public.tareas
    ADD COLUMN IF NOT EXISTS max_archivos INTEGER NOT NULL DEFAULT 10;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_max_archivos'
          AND conrelid = 'public.tareas'::regclass
    ) THEN
        ALTER TABLE public.tareas
            ADD CONSTRAINT chk_max_archivos CHECK (max_archivos >= 1);
    END IF;
END
$$;

COMMENT ON COLUMN public.tareas.max_archivos IS
    'Máximo de archivos permitidos en la tarea (1..10). Tope fijo del sistema: 10.';

COMMIT;
