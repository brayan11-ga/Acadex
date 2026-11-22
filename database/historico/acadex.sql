-- HISTORICAL ONLY: the active schema history is Alembic under backend/alembic/.
-- Kept as a record of the former manual setup; do not use for new installations
-- or updates because it does not write an Alembic revision to alembic_version.
\set ON_ERROR_STOP on
\ir init.sql
-- The dump clears search_path. The historical migrations use unqualified names.
SET search_path TO public;
\ir 20261011_add_archivo_uploader.sql
\ir 20261011_add_registration_consents.sql
\ir 20261012_add_gemini_usage_limits.sql
\ir 20261012_add_gemini_quota_lockout.sql
\ir 20261012_add_security_guards.sql
