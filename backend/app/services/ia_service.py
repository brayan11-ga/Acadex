# Ruta: backend/app/services/ia_service.py
import json
import logging
import math
import re
from datetime import datetime, timezone

import httpx
import pdfplumber
from fastapi import UploadFile, HTTPException, status
from google import genai
from google.genai import types
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.schemas.tarea import TareaPropuestaIA
from app.models.categoria import Categoria
from app.config.settings import settings
from app.services import gemini_config
from app.services import groq_service
from app.core.ia_usage_guard import (
    bloquear_hasta_reinicio_cuota_google,
    consumir_cupo_analisis,
    liberar_cupo_usuario_analisis,
    verificar_bloqueo_cuota_google,
)

logger = logging.getLogger(__name__)


class RespuestaGeminiIncompletaError(ValueError):
    """La respuesta del modelo llegó vacía o alcanzó el límite de salida."""


def _es_error_limite_gemini(error: Exception) -> bool:
    return str(getattr(error, "code", "")) == "429"


def _codigo_http(error: Exception) -> int | None:
    codigo = getattr(error, "code", None)
    if codigo is None:
        codigo = getattr(error, "status_code", None)
    try:
        return int(codigo)
    except (TypeError, ValueError):
        return None


def _es_error_gemini_recuperable(error: Exception) -> bool:
    if isinstance(
        error,
        (
            RespuestaGeminiIncompletaError,
            json.JSONDecodeError,
            ValidationError,
            TypeError,
        ),
    ):
        return True
    if isinstance(error, httpx.RequestError):
        return True
    codigo = _codigo_http(error)
    return codigo in {408, 409, 425, 429} or (
        codigo is not None and 500 <= codigo < 600
    )


def _registrar_error_groq(error: Exception) -> None:
    codigo = _codigo_http(error)
    logger.warning(
        "Falló la solicitud de respaldo: tipo_excepcion=%s codigo_groq=%s",
        type(error).__name__,
        str(codigo) if codigo is not None else "no_disponible",
    )


def _crear_propuesta_ia(texto_respuesta: str, valid_categoria_ids: list[int]):
    datos_json = json.loads(
        gemini_config.extraer_json_de_respuesta(texto_respuesta)
    )
    propuesta = TareaPropuestaIA(**datos_json)
    if (
        propuesta.id_categoria is not None
        and propuesta.id_categoria not in valid_categoria_ids
    ):
        propuesta.id_categoria = None
    return propuesta


def _analizar_con_groq(prompt: str, valid_categoria_ids: list[int]):
    try:
        texto_respuesta = groq_service.generar_respuesta(prompt)
        return _crear_propuesta_ia(texto_respuesta, valid_categoria_ids)
    except Exception as error:
        _registrar_error_groq(error)
        raise


def _error_http_gemini(error: Exception, bloqueado_hasta=None) -> HTTPException:
    if _es_cuota_diaria_agotada(error):
        if bloqueado_hasta is None:
            raise RuntimeError("Falta registrar el bloqueo diario de Gemini")
        segundos_hasta_reinicio = max(
            1,
            math.ceil(
                (bloqueado_hasta - datetime.now(timezone.utc)).total_seconds()
            ),
        )
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Se agotó la cuota gratuita diaria de Google para la demostración. "
                "El análisis volverá a estar disponible después del reinicio diario."
            ),
            headers={"Retry-After": str(segundos_hasta_reinicio)},
        )

    if _es_error_limite_gemini(error):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Google limitó temporalmente las solicitudes. Espera antes de "
                "volver a intentarlo."
            ),
            headers={"Retry-After": str(_retry_after_segundos(error))},
        )

    if isinstance(
        error,
        (
            RespuestaGeminiIncompletaError,
            json.JSONDecodeError,
            ValidationError,
            TypeError,
        ),
    ):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La IA devolvió una respuesta incompleta o inválida. Intenta nuevamente.",
        )

    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="El servicio de IA no está disponible en este momento.",
    )


def _registrar_error_gemini(
    error: Exception, finish_reason, texto_respuesta: str
) -> None:
    codigo = getattr(error, "code", None)
    if isinstance(codigo, int) and not isinstance(codigo, bool):
        codigo_log = str(codigo)
    elif isinstance(codigo, str) and codigo.isdecimal():
        codigo_log = codigo
    else:
        codigo_log = "no_disponible"

    nombre_finish_reason = getattr(finish_reason, "name", None)
    if not isinstance(nombre_finish_reason, str):
        nombre_finish_reason = "no_disponible"

    logger.warning(
        "Falló la solicitud a Gemini: tipo_excepcion=%s codigo_gemini=%s "
        "finish_reason=%s longitud_respuesta=%d",
        type(error).__name__,
        codigo_log,
        nombre_finish_reason,
        len(texto_respuesta),
    )


def _es_cuota_diaria_agotada(error: Exception) -> bool:
    """Reconoce errores RPD sin confundirlos con límites temporales por minuto."""
    if not _es_error_limite_gemini(error):
        return False

    contenido = json.dumps(
        {
            "message": getattr(error, "message", ""),
            "details": getattr(error, "details", None),
        },
        ensure_ascii=True,
        default=str,
    ).lower()
    compacto = re.sub(r"[^a-z0-9]+", "", contenido)
    if any(
        marcador in compacto
        for marcador in (
            "requestsperday",
            "perday",
            "dailyquota",
            "dailyrequests",
            "dailylimit",
        )
    ):
        return True

    # Algunas respuestas de Gemini solo incluyen RESOURCE_EXHAUSTED y un
    # mensaje genérico de cuota. Si identifican una ventana corta, no se abre
    # el bloqueo diario; si no, se falla de forma conservadora para no repetir
    # llamadas contra una posible cuota diaria agotada.
    if any(
        marcador in compacto
        for marcador in (
            "requestsperminute",
            "perminute",
            "toomanyrequests",
            "ratelimit",
            "retryafter",
            "retrydelay",
        )
    ):
        return False

    agotamiento_generico = "quota" in compacto and any(
        marcador in compacto
        for marcador in ("exceeded", "exhausted", "resourceexhausted")
    )
    return agotamiento_generico


def _retry_after_segundos(error: Exception) -> int:
    respuesta = getattr(error, "response", None)
    cabeceras = getattr(respuesta, "headers", {}) or {}
    retry_after = cabeceras.get("Retry-After") or cabeceras.get("retry-after")
    if retry_after:
        try:
            return max(1, math.ceil(float(retry_after)))
        except (TypeError, ValueError):
            pass

    def buscar_retry_delay(valor) -> str | None:
        if isinstance(valor, dict):
            for clave, contenido in valor.items():
                if str(clave).lower() in {"retrydelay", "retry_delay"}:
                    if isinstance(contenido, str):
                        return contenido
                encontrado = buscar_retry_delay(contenido)
                if encontrado:
                    return encontrado
        elif isinstance(valor, list):
            for contenido in valor:
                encontrado = buscar_retry_delay(contenido)
                if encontrado:
                    return encontrado
        return None

    demora = buscar_retry_delay(getattr(error, "details", None))
    if demora:
        coincidencia = re.fullmatch(r"\s*(\d+(?:\.\d+)?)s\s*", demora)
        if coincidencia:
            return max(1, math.ceil(float(coincidencia.group(1))))
    return 60


def extraer_texto_pdf(archivo: UploadFile) -> str:
    texto_extraido = ""
    caracteres_acumulados = 0
    limite_caracteres = 15000
    limite_paginas = 10

    try:
        # Asegurarse de estar al inicio del buffer antes de leer
        archivo.file.seek(0)
        # Abre el archivo directamente desde el buffer en memoria de FastAPI
        with pdfplumber.open(archivo.file) as pdf:
            for i, pagina in enumerate(pdf.pages):
                if i >= limite_paginas or caracteres_acumulados >= limite_caracteres:
                    break
                    
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_extraido += texto_pagina + "\n"
                    caracteres_acumulados += len(texto_pagina)
                    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo PDF está dañado o no se puede leer."
        )
    
    if not texto_extraido.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El PDF está vacío o es una imagen escaneada sin texto seleccionable."
        )
        
    return texto_extraido[:limite_caracteres]

def analizar_documento_con_ia(
    db: Session, archivo: UploadFile, id_usuario: int
) -> TareaPropuestaIA:
    if not settings.gemini_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de IA no está configurado.",
        )

    # Si el proyecto agotó la cuota RPD de Google, no volvemos a llamar al
    # proveedor hasta su reinicio diario. Si Groq está configurado, se usa como
    # respaldo mientras siga vigente ese bloqueo compartido por BD.
    bloqueo_google_previo = None
    try:
        verificar_bloqueo_cuota_google(db)
    except HTTPException as error_bloqueo:
        if error_bloqueo.status_code != status.HTTP_429_TOO_MANY_REQUESTS:
            raise
        if not settings.groq_api_key.strip():
            raise
        bloqueo_google_previo = error_bloqueo

    texto = extraer_texto_pdf(archivo)

    # Consultar las categorías reales
    categorias = db.query(Categoria).all()
    valid_categoria_ids = [c.id_categoria for c in categorias]
    
    if not categorias:
        categorias_info = "Actualmente no hay categorías. Devuelve id_categoria: 0."
    else:
        lista_cats = "\n".join([f"- ID: {c.id_categoria}, Nombre: '{c.nombre_categoria}'" for c in categorias])
        categorias_info = (
            f"El campo 'id_categoria' debe ser EXACTAMENTE uno de los siguientes IDs:\n{lista_cats}\n"
            "Si el documento no encaja claramente en ninguna categoría disponible, devuelve 0. NUNCA inventes un ID."
        )

    prompt = gemini_config.crear_prompt_analisis(texto, categorias_info)

    # Reserva el cupo antes de llamar a Google. La reserva persiste entre
    # reinicios y es compartida por todas las instancias del backend.
    consumir_cupo_analisis(db, id_usuario)

    if bloqueo_google_previo is not None:
        try:
            return _analizar_con_groq(prompt, valid_categoria_ids)
        except Exception:
            liberar_cupo_usuario_analisis(db, id_usuario)
            raise bloqueo_google_previo from None

    respuesta = None
    texto_respuesta = ""
    finish_reason = None
    try:
        with genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=1)
            ),
        ) as cliente:
            respuesta = cliente.models.generate_content(
                model=gemini_config.MODELO_GEMINI,
                contents=prompt,
                config=gemini_config.crear_configuracion_generacion(
                    max_output_tokens=gemini_config.MAX_OUTPUT_TOKENS_GEMINI,
                    thinking_config=gemini_config.THINKING_CONFIG_GEMINI,
                ),
            )
        candidatos = getattr(respuesta, "candidates", None) or []
        finish_reason = candidatos[0].finish_reason if candidatos else None
        texto_respuesta = getattr(respuesta, "text", None) or ""
        if (
            finish_reason == types.FinishReason.MAX_TOKENS
            or not texto_respuesta.strip()
        ):
            raise RespuestaGeminiIncompletaError(
                "Gemini no completó la respuesta"
            )
        return _crear_propuesta_ia(texto_respuesta, valid_categoria_ids)
    except Exception as error:
        # Registrar metadatos seguros; nunca contenido de solicitud o respuesta.
        _registrar_error_gemini(error, finish_reason, texto_respuesta)
        bloqueado_hasta = None
        if _es_cuota_diaria_agotada(error):
            try:
                bloqueado_hasta = bloquear_hasta_reinicio_cuota_google(db)
            except HTTPException:
                liberar_cupo_usuario_analisis(db, id_usuario)
                raise

        if (
            settings.groq_api_key.strip()
            and _es_error_gemini_recuperable(error)
        ):
            try:
                return _analizar_con_groq(prompt, valid_categoria_ids)
            except Exception:
                liberar_cupo_usuario_analisis(db, id_usuario)
                raise _error_http_gemini(error, bloqueado_hasta) from None

        liberar_cupo_usuario_analisis(db, id_usuario)
        raise _error_http_gemini(error, bloqueado_hasta) from None
