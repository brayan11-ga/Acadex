-- Bloqueo persistente del análisis cuando Google informa que se agotó la cuota RPD.
-- No almacena documentos, respuestas ni mensajes del proveedor.
BEGIN;

CREATE TABLE IF NOT EXISTS bloqueo_cuota_gemini (
    id VARCHAR(32) PRIMARY KEY,
    bloqueado_hasta TIMESTAMPTZ NOT NULL,
    CONSTRAINT ck_bloqueo_cuota_gemini_id
        CHECK (id = 'proyecto')
);

COMMIT;
