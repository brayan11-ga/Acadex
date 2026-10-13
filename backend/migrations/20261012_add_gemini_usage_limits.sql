-- Contadores mínimos para limitar las llamadas a Gemini por usuario y por día.
-- No almacena contenido de documentos ni respuestas generadas.
BEGIN;

CREATE TABLE IF NOT EXISTS uso_analisis_ia (
    fecha_utc DATE NOT NULL,
    alcance VARCHAR(10) NOT NULL,
    identificador_alcance VARCHAR(64) NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT pk_uso_analisis_ia
        PRIMARY KEY (fecha_utc, alcance, identificador_alcance),
    CONSTRAINT ck_uso_analisis_ia_cantidad
        CHECK (cantidad >= 0),
    CONSTRAINT ck_uso_analisis_ia_alcance
        CHECK (
            (alcance = 'usuario' AND identificador_alcance <> '')
            OR (alcance = 'global' AND identificador_alcance = 'global')
        )
);

COMMIT;
