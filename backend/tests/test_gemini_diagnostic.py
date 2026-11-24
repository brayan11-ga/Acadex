import unittest
from unittest.mock import Mock

from google.genai import types

from app.services.gemini_diagnostic import crear_resumen_diagnostico


class DiagnosticoGeminiTests(unittest.TestCase):
    def test_respuesta_sin_candidatos_informa_que_no_hay_finish_reason(self):
        respuesta = Mock(spec=["candidates", "text", "usage_metadata"])
        respuesta.candidates = []
        respuesta.text = None
        respuesta.usage_metadata = None

        resumen = crear_resumen_diagnostico(respuesta)

        self.assertEqual(resumen["finish_reason"], "sin_candidatos")
        self.assertEqual(resumen["longitud_respuesta"], 0)
        self.assertEqual(resumen["tokens_razonamiento"], "no_disponible")
        self.assertEqual(resumen["tokens_salida"], "no_disponible")
        self.assertEqual(resumen["json_valido"], "no")

    def test_respuesta_con_metadatos_ausentes_conserva_finish_reason(self):
        respuesta = Mock(spec=["candidates", "text", "usage_metadata"])
        respuesta.candidates = [Mock(finish_reason=types.FinishReason.STOP)]
        respuesta.text = '{"titulo":"Ciclo del agua"}'
        respuesta.usage_metadata = None

        resumen = crear_resumen_diagnostico(respuesta)

        self.assertEqual(resumen["finish_reason"], "STOP")
        self.assertEqual(resumen["longitud_respuesta"], len(respuesta.text))
        self.assertEqual(resumen["tokens_razonamiento"], "no_disponible")
        self.assertEqual(resumen["tokens_salida"], "no_disponible")
        self.assertEqual(resumen["json_valido"], "sí")

    def test_metadata_sin_conteo_razonamiento_muestra_salida_disponible(self):
        uso = Mock(spec=["candidates_token_count"])
        uso.candidates_token_count = 19
        respuesta = Mock(spec=["candidates", "text", "usage_metadata"])
        respuesta.candidates = [Mock(finish_reason=types.FinishReason.STOP)]
        respuesta.text = '{"titulo":"Ciclo del agua"}'
        respuesta.usage_metadata = uso

        resumen = crear_resumen_diagnostico(respuesta)

        self.assertEqual(resumen["tokens_razonamiento"], "no_disponible")
        self.assertEqual(resumen["tokens_salida"], 19)

    def test_finish_reason_en_texto_se_conserva(self):
        respuesta = Mock(spec=["candidates", "text", "usage_metadata"])
        respuesta.candidates = [Mock(finish_reason="MAX_TOKENS")]
        respuesta.text = ""
        respuesta.usage_metadata = None

        resumen = crear_resumen_diagnostico(respuesta)

        self.assertEqual(resumen["finish_reason"], "MAX_TOKENS")

    def test_error_de_api_se_clasifica_sin_imprimir_mensaje(self):
        error = RuntimeError("detalle con secreto que no debe salir")
        error.code = 400

        resumen = crear_resumen_diagnostico(None, error)

        self.assertEqual(resumen["finish_reason"], "error_http_400")
        self.assertNotIn("secreto", str(resumen))


if __name__ == "__main__":
    unittest.main()
