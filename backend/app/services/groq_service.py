"""Adaptador de Groq. Recibe texto extraído del PDF, nunca bytes del archivo."""

from app.config.settings import MODELO_GROQ_POR_DEFECTO, settings
from app.services import gemini_config


MAX_COMPLETION_TOKENS_GROQ = 2048
REASONING_EFFORT_GROQ = "low"


class RespuestaGroqIncompletaError(ValueError):
    """La respuesta de Groq llegó vacía o se truncó por límite de tokens."""


def _crear_cliente(api_key: str):
    # Import diferido: el backend solo carga el SDK si se activa el respaldo.
    from groq import Groq

    return Groq(api_key=api_key, max_retries=0, timeout=30.0)


def generar_respuesta(prompt: str) -> str:
    esquema = {
        **gemini_config.ESQUEMA_PROPUESTA_IA,
        "additionalProperties": False,
    }
    with _crear_cliente(settings.groq_api_key) as cliente:
        respuesta = cliente.chat.completions.create(
            model=settings.groq_model or MODELO_GROQ_POR_DEFECTO,
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "propuesta_tarea_acadex",
                    "strict": True,
                    "schema": esquema,
                },
            },
            max_completion_tokens=MAX_COMPLETION_TOKENS_GROQ,
            reasoning_effort=REASONING_EFFORT_GROQ,
        )

    elecciones = getattr(respuesta, "choices", None) or []
    if not elecciones:
        raise RespuestaGroqIncompletaError("Groq no devolvió opciones")

    opcion = elecciones[0]
    mensaje = getattr(opcion, "message", None)
    texto = getattr(mensaje, "content", None)
    if getattr(opcion, "finish_reason", None) == "length":
        raise RespuestaGroqIncompletaError("Groq alcanzó el límite de salida")
    if not isinstance(texto, str) or not texto.strip():
        raise RespuestaGroqIncompletaError("Groq devolvió una respuesta vacía")

    return texto
