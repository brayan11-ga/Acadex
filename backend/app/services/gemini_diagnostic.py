import json

from app.services.gemini_config import extraer_json_de_respuesta


def crear_resumen_diagnostico(respuesta, error=None) -> dict[str, int | str]:
    if error is not None:
        codigo = getattr(error, "code", None)
        if isinstance(codigo, int) and not isinstance(codigo, bool):
            finish_reason = f"error_http_{codigo}"
        elif isinstance(codigo, str) and codigo.isdecimal():
            finish_reason = f"error_http_{codigo}"
        else:
            finish_reason = f"error_{type(error).__name__}"
    elif respuesta is None:
        finish_reason = "no_disponible"
    else:
        candidatos = getattr(respuesta, "candidates", None) or []
        if not candidatos:
            finish_reason = "sin_candidatos"
        else:
            motivo = getattr(candidatos[0], "finish_reason", None)
            finish_reason = getattr(motivo, "name", None)
            if not finish_reason and motivo is not None:
                finish_reason = str(motivo)
            finish_reason = finish_reason or "no_disponible"

    texto = getattr(respuesta, "text", None) or ""
    uso = getattr(respuesta, "usage_metadata", None)
    tokens_razonamiento = getattr(uso, "thoughts_token_count", None)
    tokens_salida = getattr(uso, "candidates_token_count", None)

    try:
        json.loads(extraer_json_de_respuesta(texto))
        json_valido = "sí"
    except (json.JSONDecodeError, TypeError):
        json_valido = "no"

    return {
        "finish_reason": finish_reason,
        "longitud_respuesta": len(texto),
        "tokens_razonamiento": (
            tokens_razonamiento
            if tokens_razonamiento is not None
            else "no_disponible"
        ),
        "tokens_salida": (
            tokens_salida if tokens_salida is not None else "no_disponible"
        ),
        "json_valido": json_valido,
    }
