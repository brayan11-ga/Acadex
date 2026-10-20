"""Diagnóstico manual; no se ejecuta en pruebas automáticas ni en CI."""

import argparse
import os

from google import genai
from google.genai import types

from app.services import gemini_config
from app.services.gemini_diagnostic import crear_resumen_diagnostico


TEXTO_EJEMPLO = "Preparar un resumen corto sobre el ciclo del agua."
CATEGORIAS_EJEMPLO = "Actualmente no hay categorías. Devuelve id_categoria: 0."


def _argumentos():
    parser = argparse.ArgumentParser(
        description="Prueba manual de configuración de Gemini."
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=gemini_config.MAX_OUTPUT_TOKENS_GEMINI,
    )
    thinking = parser.add_mutually_exclusive_group()
    thinking.add_argument("--thinking-budget", type=int)
    thinking.add_argument(
        "--thinking-level",
        choices=("minimal", "low", "medium", "high"),
    )
    return parser.parse_args()


def main() -> int:
    args = _argumentos()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Define GEMINI_API_KEY en el entorno antes de ejecutar.")

    thinking_config = gemini_config.THINKING_CONFIG_GEMINI
    if args.thinking_budget is not None:
        thinking_config = types.ThinkingConfig(
            thinking_budget=args.thinking_budget
        )
    elif args.thinking_level is not None:
        thinking_config = types.ThinkingConfig(thinking_level=args.thinking_level)

    respuesta = None
    error_solicitud = None
    try:
        with genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=1)
            ),
        ) as cliente:
            respuesta = cliente.models.generate_content(
                model=gemini_config.MODELO_GEMINI,
                contents=gemini_config.crear_prompt_analisis(
                    TEXTO_EJEMPLO,
                    CATEGORIAS_EJEMPLO,
                ),
                config=gemini_config.crear_configuracion_generacion(
                    max_output_tokens=args.max_output_tokens,
                    thinking_config=thinking_config,
                ),
            )
    except Exception as error:
        error_solicitud = error

    resumen = crear_resumen_diagnostico(respuesta, error_solicitud)
    for campo, valor in resumen.items():
        print(f"{campo}: {valor}")
    return 1 if error_solicitud is not None else 0


if __name__ == "__main__":
    raise SystemExit(main())
