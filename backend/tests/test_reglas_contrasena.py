import pytest
from pydantic import ValidationError

from app.schemas.auth import ResetPasswordIn
from app.schemas.contrasena import LONGITUD_MINIMA_CONTRASENA
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


def datos_registro(contrasena: str) -> dict[str, object]:
    return {
        "correo_electronico": "persona@example.com",
        "contrasena": contrasena,
        "acepta_tratamiento_datos": True,
        "confirma_aviso_almacenamiento": True,
    }


def test_registro_actualizacion_y_reset_aceptan_el_limite_minimo():
    contrasena = "x" * LONGITUD_MINIMA_CONTRASENA

    assert UsuarioCreate(**datos_registro(contrasena)).contrasena == contrasena
    assert UsuarioUpdate(contrasena=contrasena).contrasena == contrasena
    assert ResetPasswordIn(token="token-sintetico", nueva_contrasena=contrasena)


@pytest.mark.parametrize(
    "crear_modelo",
    [
        lambda contrasena: UsuarioCreate(**datos_registro(contrasena)),
        lambda contrasena: UsuarioUpdate(contrasena=contrasena),
        lambda contrasena: ResetPasswordIn(
            token="token-sintetico",
            nueva_contrasena=contrasena,
        ),
    ],
    ids=["registro", "actualizacion-admin", "reset"],
)
def test_los_tres_flujos_rechazan_menos_de_ocho_caracteres(crear_modelo):
    contrasena_corta = "x" * (LONGITUD_MINIMA_CONTRASENA - 1)

    with pytest.raises(ValidationError):
        crear_modelo(contrasena_corta)


def test_los_tres_flujos_rechazan_ocho_espacios():
    contrasena_vacia = " " * LONGITUD_MINIMA_CONTRASENA

    with pytest.raises(ValidationError):
        UsuarioCreate(**datos_registro(contrasena_vacia))
    with pytest.raises(ValidationError):
        UsuarioUpdate(contrasena=contrasena_vacia)
    with pytest.raises(ValidationError):
        ResetPasswordIn(token="token-sintetico", nueva_contrasena=contrasena_vacia)
