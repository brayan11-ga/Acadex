-- Ruta: database/migrations/20261110_add_sesion_cronometro_por_usuario.sql
-- Migración manual (Supabase / psql): un cronómetro activo por (tarea, usuario).
-- Equivale a la revisión Alembic 20261110_01_sesion_cronometro_por_usuario.py.
-- Idempotente: se puede ejecutar más de una vez sin error.
-- Orden de despliegue: aplicar este SQL ANTES del código nuevo. La regla nueva es
-- menos estricta que la anterior, así que no rompe filas existentes.
BEGIN;

DROP INDEX IF EXISTS public.uq_sesiones_tarea_activa;

CREATE UNIQUE INDEX IF NOT EXISTS uq_sesiones_tarea_activa
    ON public.sesiones_cronometro (id_tarea, id_usuario)
    WHERE fecha_fin IS NULL;

COMMIT;
