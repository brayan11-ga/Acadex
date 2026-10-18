from typing import Annotated

from pydantic import AfterValidator, Field


LONGITUD_MINIMA_CONTRASENA = 8


def _validar_contrasena_no_vacia(valor: str) -> str:
    if not valor.strip():
        raise ValueError("La contraseña no puede estar vacía")
    return valor


Contrasena = Annotated[
    str,
    Field(min_length=LONGITUD_MINIMA_CONTRASENA),
    AfterValidator(_validar_contrasena_no_vacia),
]
