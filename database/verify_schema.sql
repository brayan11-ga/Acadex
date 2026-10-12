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
    ) AS autor_archivo_fk_set_null;
