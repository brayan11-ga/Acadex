-- No elimina evidencia de aceptación. Exporte y gestione esos registros antes
-- de una reversión que retire esta tabla.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM consentimientos_usuario LIMIT 1) THEN
        RAISE EXCEPTION 'La tabla contiene evidencia de aceptación; expórtela antes de retirar el esquema.';
    END IF;
END
$$;

DROP TABLE consentimientos_usuario;
