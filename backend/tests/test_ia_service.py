# Ruta: backend/tests/test_ia_service.py
import json
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.bloqueo_cuota_gemini import BloqueoCuotaGemini
from app.models.uso_analisis_ia import UsoAnalisisIA
from app.services import ia_service


class ServicioGeminiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Categoria.__table__.create(self.engine)
        UsoAnalisisIA.__table__.create(self.engine)
        BloqueoCuotaGemini.__table__.create(self.engine)
        self.db = Session(self.engine)
        self.db.add(Categoria(id_categoria=7, nombre_categoria="Ciencias"))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _cliente_falso(self, respuesta):
        cliente = MagicMock()
        cliente.__enter__.return_value = cliente
        cliente.__exit__.return_value = False
        cliente.models.generate_content.return_value = respuesta
        return cliente

    def _respuesta_valida(self, id_categoria=7):
        return self._respuesta_con_texto(
            json.dumps(
                {
                    "titulo": "Taller de ciencias",
                    "descripcion": "Resolver los ejercicios del documento.",
                    "dificultad_estimada": 3,
                    "tiempo_estimado": 60,
                    "id_categoria": id_categoria,
                }
            )
        )

    def _respuesta_con_texto(
        self, texto, finish_reason=ia_service.types.FinishReason.STOP
    ):
        return SimpleNamespace(
            text=texto,
            candidates=[SimpleNamespace(finish_reason=finish_reason)],
        )

    def test_respuesta_vacia_con_max_tokens_es_error_controlado(self):
        cliente = self._cliente_falso(
            self._respuesta_con_texto(
                "", ia_service.types.FinishReason.MAX_TOKENS
            )
        )
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(ia_service.genai, "Client", return_value=cliente),
        ):
            with self.assertRaises(HTTPException) as error:
                ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertEqual(error.exception.status_code, 502)
        self.assertIn("incompleta", error.exception.detail.lower())

    def test_json_cortado_por_max_tokens_es_error_controlado(self):
        cliente = self._cliente_falso(
            self._respuesta_con_texto(
                '{"titulo":"Taller de ciencias",',
                ia_service.types.FinishReason.MAX_TOKENS,
            )
        )
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(ia_service.genai, "Client", return_value=cliente),
        ):
            with self.assertRaises(HTTPException) as error:
                ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertEqual(error.exception.status_code, 502)
        self.assertIn("incompleta", error.exception.detail.lower())

    def test_json_completo_en_bloque_json_se_analiza(self):
        contenido = self._respuesta_valida().text
        cliente = self._cliente_falso(
            self._respuesta_con_texto(f"```json\n{contenido}\n```")
        )
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(ia_service.genai, "Client", return_value=cliente),
        ):
            propuesta = ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertEqual(propuesta.titulo, "Taller de ciencias")
        self.assertEqual(propuesta.id_categoria, 7)

    def test_envia_una_solicitud_estructurada_y_valida_la_categoria(self):
        cliente = self._cliente_falso(self._respuesta_valida())
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(ia_service.genai, "Client", return_value=cliente) as crear_cliente,
        ):
            propuesta = ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertEqual(propuesta.titulo, "Taller de ciencias")
        self.assertEqual(propuesta.id_categoria, 7)
        crear_cliente.assert_called_once()
        self.assertEqual(
            crear_cliente.call_args.kwargs["api_key"], "clave-sintetica"
        )
        self.assertEqual(
            crear_cliente.call_args.kwargs["http_options"].retry_options.attempts,
            1,
        )
        solicitud = cliente.models.generate_content.call_args.kwargs
        self.assertEqual(solicitud["model"], "gemini-3.6-flash")
        self.assertEqual(solicitud["config"].response_mime_type, "application/json")
        self.assertEqual(
            solicitud["config"].response_json_schema,
            ia_service.gemini_config.ESQUEMA_PROPUESTA_IA,
        )
        self.assertEqual(
            solicitud["config"].max_output_tokens,
            ia_service.gemini_config.MAX_OUTPUT_TOKENS_GEMINI,
        )
        self.assertEqual(
            solicitud["config"].thinking_config,
            ia_service.gemini_config.THINKING_CONFIG_GEMINI,
        )

    def test_envia_thinking_y_limite_de_tokens_configurados(self):
        cliente = self._cliente_falso(self._respuesta_valida())
        thinking_config = ia_service.types.ThinkingConfig(
            thinking_level="minimal"
        )
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(
                ia_service.gemini_config,
                "MAX_OUTPUT_TOKENS_GEMINI",
                2048,
            ),
            patch.object(
                ia_service.gemini_config,
                "THINKING_CONFIG_GEMINI",
                thinking_config,
            ),
            patch.object(ia_service.genai, "Client", return_value=cliente),
        ):
            ia_service.analizar_documento_con_ia(self.db, None, 41)

        config = cliente.models.generate_content.call_args.kwargs["config"]
        self.assertEqual(config.max_output_tokens, 2048)
        self.assertEqual(
            config.thinking_config.thinking_level,
            ia_service.types.ThinkingLevel.MINIMAL,
        )

    def test_categoria_inventada_se_descarta(self):
        cliente = self._cliente_falso(self._respuesta_valida(id_categoria=9999))
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(ia_service.genai, "Client", return_value=cliente),
        ):
            propuesta = ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertIsNone(propuesta.id_categoria)

    def test_respuesta_invalida_falla_sin_exponer_detalles(self):
        cliente = self._cliente_falso(SimpleNamespace(text='{"titulo": 42}'))
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(ia_service.genai, "Client", return_value=cliente),
        ):
            with self.assertLogs("app.services.ia_service", level="WARNING") as logs:
                with self.assertRaises(HTTPException) as error:
                    ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertEqual(error.exception.status_code, 502)
        self.assertNotIn("Contenido sintético", "\n".join(logs.output))
        fecha_utc = datetime.now(timezone.utc).date()
        contador_usuario = self.db.get(UsoAnalisisIA, (fecha_utc, "usuario", "41"))
        self.assertEqual(contador_usuario.cantidad, 0)

    def test_error_del_proveedor_se_sanitiza(self):
        cliente = self._cliente_falso(self._respuesta_valida())
        cliente.models.generate_content.side_effect = RuntimeError("texto privado del proveedor")
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(ia_service.genai, "Client", return_value=cliente),
        ):
            with self.assertLogs("app.services.ia_service", level="WARNING") as logs:
                with self.assertRaises(HTTPException) as error:
                    ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertEqual(error.exception.status_code, 503)
        self.assertNotIn("texto privado del proveedor", "\n".join(logs.output))

    def test_log_registra_metadatos_sin_contenido_del_pdf_ni_respuesta(self):
        texto_pdf_privado = "PDF_PRIVADO_NO_DEBE_APARECER"
        texto_respuesta_privado = "RESPUESTA_PRIVADA_NO_DEBE_APARECER"
        cliente = self._cliente_falso(
            self._respuesta_con_texto(
                texto_respuesta_privado,
                ia_service.types.FinishReason.MAX_TOKENS,
            )
        )
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value=texto_pdf_privado),
            patch.object(ia_service.genai, "Client", return_value=cliente),
        ):
            with self.assertLogs("app.services.ia_service", level="WARNING") as logs:
                with self.assertRaises(HTTPException) as error:
                    ia_service.analizar_documento_con_ia(self.db, None, 41)

        salida_log = "\n".join(logs.output)
        self.assertEqual(error.exception.status_code, 502)
        self.assertIn("tipo_excepcion=RespuestaGeminiIncompletaError", salida_log)
        self.assertIn("codigo_gemini=no_disponible", salida_log)
        self.assertIn("finish_reason=MAX_TOKENS", salida_log)
        self.assertIn(
            f"longitud_respuesta={len(texto_respuesta_privado)}", salida_log
        )
        self.assertNotIn(texto_pdf_privado, salida_log)
        self.assertNotIn(texto_respuesta_privado, salida_log)
        self.assertNotIn("clave-sintetica", salida_log)

    def test_clave_ausente_no_llama_a_google_ni_consumo_cupo(self):
        with (
            patch.object(ia_service.settings, "gemini_api_key", "  "),
            patch.object(ia_service.genai, "Client") as crear_cliente,
            patch.object(ia_service, "consumir_cupo_analisis") as consumir_cupo,
        ):
            with self.assertRaises(HTTPException) as error:
                ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertEqual(error.exception.status_code, 503)
        crear_cliente.assert_not_called()
        consumir_cupo.assert_not_called()

    def test_cupo_agotado_impide_llamar_a_google(self):
        cliente = self._cliente_falso(self._respuesta_valida())
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(
                ia_service,
                "consumir_cupo_analisis",
                side_effect=HTTPException(status_code=429, detail="Límite agotado"),
            ),
            patch.object(ia_service.genai, "Client", return_value=cliente) as crear_cliente,
        ):
            with self.assertRaises(HTTPException) as error:
                ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertEqual(error.exception.status_code, 429)
        crear_cliente.assert_not_called()

    def test_cuota_diaria_de_google_bloquea_el_proyecto_hasta_el_reinicio(self):
        cliente = self._cliente_falso(self._respuesta_valida())
        error_google = RuntimeError("respuesta sintética de cuota")
        error_google.code = 429
        error_google.message = "Quota exceeded"
        error_google.details = {
            "error": {
                "details": [
                    {
                        "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
                        "quotaValue": "20",
                    }
                ]
            }
        }
        cliente.models.generate_content.side_effect = error_google
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(ia_service.genai, "Client", return_value=cliente) as crear_cliente,
        ):
            with self.assertRaises(HTTPException) as error:
                ia_service.analizar_documento_con_ia(self.db, None, 41)

            self.assertEqual(error.exception.status_code, 429)
            self.assertIn("Retry-After", error.exception.headers)
            self.assertIsNotNone(self.db.get(BloqueoCuotaGemini, "proyecto"))

            with patch.object(ia_service, "extraer_texto_pdf") as extraer_pdf:
                with self.assertRaises(HTTPException) as segundo_error:
                    ia_service.analizar_documento_con_ia(self.db, None, 42)

            self.assertEqual(segundo_error.exception.status_code, 429)
            extraer_pdf.assert_not_called()
            crear_cliente.assert_called_once()

    def test_limite_por_minuto_no_bloquea_la_cuota_diaria(self):
        cliente = self._cliente_falso(self._respuesta_valida())
        error_google = RuntimeError("respuesta sintética de límite temporal")
        error_google.code = 429
        error_google.message = "Rate limit exceeded"
        error_google.details = {
            "error": {
                "details": [
                    {"quotaId": "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"}
                ]
            }
        }
        cliente.models.generate_content.side_effect = error_google
        with (
            patch.object(ia_service.settings, "gemini_api_key", "clave-sintetica"),
            patch.object(ia_service, "extraer_texto_pdf", return_value="Contenido sintético"),
            patch.object(ia_service.genai, "Client", return_value=cliente),
        ):
            with self.assertRaises(HTTPException) as error:
                ia_service.analizar_documento_con_ia(self.db, None, 41)

        self.assertEqual(error.exception.status_code, 429)
        self.assertEqual(error.exception.headers["Retry-After"], "60")
        self.assertIsNone(self.db.get(BloqueoCuotaGemini, "proyecto"))
        fecha_utc = datetime.now(timezone.utc).date()
        self.assertEqual(
            self.db.get(UsoAnalisisIA, (fecha_utc, "usuario", "41")).cantidad,
            0,
        )


if __name__ == "__main__":
    unittest.main()
