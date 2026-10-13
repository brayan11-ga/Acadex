from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.request_guard import limitar_solicitudes


VENTANA_SEGUNDOS = 60 * 60
MAX_INTENTOS = 50


def registrar_intento(identificador_cliente: str, db: Session | None = None) -> None:
    """Límite de registro persistente y compartido entre instancias."""
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El registro no está disponible temporalmente.",
        )
    limitar_solicitudes(
        db,
        "registro_ip",
        identificador_cliente,
        maximo=MAX_INTENTOS,
        ventana_segundos=VENTANA_SEGUNDOS,
        mensaje="Se alcanzó el límite temporal de registros desde esta conexión.",
    )
