-- Solo revierte si aún no se han guardado autores nuevos.
-- Si la comprobación falla, exporte primero esos datos y revise el rollback manualmente.
BEGIN;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM archivos WHERE id_usuario_subida IS NOT NULL) THEN
        RAISE EXCEPTION 'El rollback eliminaría autorías. Exporte los datos y revise la operación antes de continuar.';
    END IF;
END
$$;

ALTER TABLE archivos DROP CONSTRAINT IF EXISTS fk_archivos_usuario_subida;
ALTER TABLE archivos DROP COLUMN IF EXISTS id_usuario_subida;

COMMIT;
