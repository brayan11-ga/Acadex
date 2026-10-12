-- Compatibility entrypoint for the historical manual setup command.
-- The canonical baseline is database/init.sql; later changes remain in the
-- versioned SQL files under backend/migrations/.
\set ON_ERROR_STOP on
\ir ../init.sql
\ir ../../backend/migrations/20261011_add_archivo_uploader.sql
\ir ../../backend/migrations/20261011_add_registration_consents.sql
