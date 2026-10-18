-- HISTORICAL ONLY: the active schema history is Alembic under backend/alembic/.
-- Kept as a record of the former manual setup; do not use for new installations
-- or updates because it does not write an Alembic revision to alembic_version.
\set ON_ERROR_STOP on
\ir ../init.sql
\ir ../../backend/migrations/20261011_add_archivo_uploader.sql
\ir ../../backend/migrations/20261011_add_registration_consents.sql
\ir ../../backend/migrations/20261012_add_gemini_usage_limits.sql
\ir ../../backend/migrations/20261012_add_gemini_quota_lockout.sql
\ir ../../backend/migrations/20261012_add_security_guards.sql
