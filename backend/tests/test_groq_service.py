import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services import gemini_config, groq_service


class ServicioGroqTests(unittest.TestCase):
    def test_cliente_sdk_se_crea_sin_enviar_solicitudes(self):
        cliente = groq_service._crear_cliente("clave-sintetica")
        try:
            self.assertIsNotNone(cliente)
        finally:
            cliente.close()

    def test_envia_prompt_esquema_y_limites_configurados(self):
        cliente = MagicMock()
        cliente.__enter__.return_value = cliente
        cliente.__exit__.return_value = False
        cliente.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    finish_reason="stop",
                    message=SimpleNamespace(content='{"titulo":"Taller"}'),
                )
            ]
        )
        prompt = "Prompt sintético con contenido de prueba"

        with (
            patch.object(groq_service.settings, "groq_api_key", "clave-sintetica"),
            patch.object(groq_service.settings, "groq_model", "modelo-sintetico"),
            patch.object(groq_service, "_crear_cliente", return_value=cliente) as crear_cliente,
        ):
            respuesta = groq_service.generar_respuesta(prompt)

        self.assertEqual(respuesta, '{"titulo":"Taller"}')
        crear_cliente.assert_called_once_with("clave-sintetica")
        solicitud = cliente.chat.completions.create.call_args.kwargs
        self.assertEqual(solicitud["model"], "modelo-sintetico")
        self.assertEqual(solicitud["messages"], [{"role": "user", "content": prompt}])
        self.assertEqual(
            solicitud["response_format"]["json_schema"]["schema"],
            {**gemini_config.ESQUEMA_PROPUESTA_IA, "additionalProperties": False},
        )
        self.assertTrue(solicitud["response_format"]["json_schema"]["strict"])
        self.assertEqual(
            solicitud["max_completion_tokens"],
            groq_service.MAX_COMPLETION_TOKENS_GROQ,
        )
        self.assertEqual(
            solicitud["reasoning_effort"], groq_service.REASONING_EFFORT_GROQ
        )

    def test_respuesta_vacia_o_truncada_se_marca_incompleta(self):
        for finish_reason, content in (("length", "{"), ("stop", " ")):
            cliente = MagicMock()
            cliente.__enter__.return_value = cliente
            cliente.__exit__.return_value = False
            cliente.chat.completions.create.return_value = SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        finish_reason=finish_reason,
                        message=SimpleNamespace(content=content),
                    )
                ]
            )
            with (
                patch.object(groq_service.settings, "groq_api_key", "clave-sintetica"),
                patch.object(groq_service, "_crear_cliente", return_value=cliente),
            ):
                with self.assertRaises(groq_service.RespuestaGroqIncompletaError):
                    groq_service.generar_respuesta("Prompt sintético")


if __name__ == "__main__":
    unittest.main()
