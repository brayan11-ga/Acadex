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
