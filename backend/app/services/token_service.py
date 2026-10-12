"""Compatibilidad para imports antiguos de generación de enlaces de reset.

La implementación canónica vive en ``usuario_service`` para que todos los
flujos invaliden tokens previos y almacenen solo su digest.
"""

from app.services.usuario_service import generar_token_reset_password

__all__ = ["generar_token_reset_password"]
