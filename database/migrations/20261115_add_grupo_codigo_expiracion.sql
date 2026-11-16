-- Ruta: database/migrations/20261115_add_grupo_codigo_expiracion.sql
-- Migración manual (Supabase / psql): vencimiento del código de acceso del grupo.
-- Equivale a la revisión Alembic 20261115_01_grupo_codigo_expiracion.py.
-- Idempotente: se puede ejecutar más de una vez sin error.
-- Orden de despliegue: aplicar este SQL ANTES del código nuevo, porque el código
-- ya consulta `fecha_expiracion_codigo`. Los grupos existentes quedan con NULL,
-- es decir, con el código vencido hasta que el líder lo regenere.
BEGIN;

ALTER TABLE public.grupos
    ADD COLUMN IF NOT EXISTS fecha_expiracion_codigo TIMESTAMP WITHOUT TIME ZONE;

COMMENT ON COLUMN public.grupos.fecha_expiracion_codigo IS
    'Vencimiento UTC del código de acceso. NULL = vencido.';

COMMIT;
