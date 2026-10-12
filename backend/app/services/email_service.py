import os 
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def enviar_reset(correo:str, token:str)->None:
    link = f"{os.getenv('FRONTEND_URL')}/restablecer-contrasena?token={token}"
    msg=EmailMessage()
    msg["Subject"]="restablecer contraseña"
    msg["From"]=os.getenv("MAIL_FROM")
    msg["TO"]=correo
    msg.set_content(f"abre este enlace para restablecer su contraseña(vence en 5min):\n={link}")
    with smtplib.SMTP(os.getenv("SMTP_HOST"),int(os.getenv("SMTP_PORT"))) as s:
        s.send(msg)