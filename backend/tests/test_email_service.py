import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services import email_service


class EmailServiceTests(unittest.TestCase):
    def test_envia_enlace_con_starttls_autenticacion_y_vencimiento_correcto(self):
        configuracion = SimpleNamespace(
            password_reset_enabled=True,
            smtp_host="smtp.example.test",
            smtp_port=587,
            smtp_username="usuario-sintetico",
            smtp_password="clave-sintetica",
            smtp_starttls=True,
            mail_from="no-reply@example.test",
            frontend_url="https://acadex.pages.dev/",
            app_env="production",
        )
        servidor = MagicMock()
        smtp = MagicMock()
        smtp.return_value.__enter__.return_value = servidor

        with (
            patch.object(email_service, "settings", configuracion),
            patch.object(email_service.smtplib, "SMTP", smtp),
            patch.object(email_service.ssl, "create_default_context", return_value="contexto-tls"),
        ):
            email_service.enviar_reset("persona@example.test", "token-sintetico")

        smtp.assert_called_once_with("smtp.example.test", 587, timeout=10)
        servidor.starttls.assert_called_once_with(context="contexto-tls")
        servidor.login.assert_called_once_with("usuario-sintetico", "clave-sintetica")
        mensaje = servidor.send_message.call_args.args[0]
        self.assertEqual(mensaje["To"], "persona@example.test")
        self.assertEqual(mensaje["From"], "no-reply@example.test")
        self.assertIn("token-sintetico", mensaje.get_content())
        self.assertIn("15 minutos", mensaje.get_content())

    def test_rechaza_envio_si_la_funcion_esta_deshabilitada(self):
        configuracion = SimpleNamespace(password_reset_enabled=False)
        with (
            patch.object(email_service, "settings", configuracion),
            patch.object(email_service.smtplib, "SMTP") as smtp,
        ):
            with self.assertRaises(RuntimeError):
                email_service.enviar_reset("persona@example.test", "token-sintetico")
        smtp.assert_not_called()


if __name__ == "__main__":
    unittest.main()
