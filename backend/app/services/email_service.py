import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode

from app.config.settings import settings


def enviar_reset(correo: str, token: str) -> None:
    if not settings.password_reset_enabled:
        raise RuntimeError("La recuperación de contraseña está deshabilitada")
    if not settings.smtp_host or not settings.mail_from or not settings.frontend_url:
        raise RuntimeError("Falta configurar el servicio de correo de recuperación")
    if bool(settings.smtp_username) != bool(settings.smtp_password):
        raise RuntimeError("La autenticación SMTP requiere usuario y contraseña")
    if settings.app_env.strip().lower() == "production" and not settings.smtp_starttls:
        raise RuntimeError("SMTP debe usar STARTTLS en producción")

    query = urlencode({"token": token})
    enlace = f"{settings.frontend_url.rstrip('/')}/restablecer-contrasena?{query}"

    mensaje = EmailMessage()
    mensaje["Subject"] = "Restablecer contraseña de ACADEX"
    mensaje["From"] = settings.mail_from
    mensaje["To"] = correo
    mensaje.set_content(
        "Usa el enlace siguiente para restablecer tu contraseña. "
        "El enlace vence en 15 minutos y solo se puede usar una vez:\n\n"
        f"{enlace}\n"
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as servidor:
        if settings.smtp_starttls:
            servidor.starttls(context=ssl.create_default_context())
        if settings.smtp_username:
            servidor.login(settings.smtp_username, settings.smtp_password)
        servidor.send_message(mensaje)
