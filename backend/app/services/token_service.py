import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario import Usuario
from app.models.token_temporal import TokenTemporal

def generar_token_reset_password(db: Session, id_usuario: int) -> TokenTemporal:
    # Verifica que el usuario exista
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # Genera un valor de token aleatorio y seguro (32 caracteres aprox)
    valor = secrets.token_urlsafe(24)

    nuevo_token = TokenTemporal(
        tipo_token="reset_password",
        valor_token=valor,
        fecha_expiracion=datetime.utcnow() + timedelta(hours=1),  # expira en 1 hora
        usado=False,
        id_usuario=id_usuario,
        id_grupo=None,
    )

    db.add(nuevo_token)
    db.commit()
    db.refresh(nuevo_token)

    return nuevo_token