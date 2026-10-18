from types import SimpleNamespace
from unittest.mock import Mock, patch

import app.models  # noqa: F401 - registra los modelos en Base.metadata
import pytest

from app.db.alembic_safety import (
    GUIA_ADOPCION,
    obtener_comando_alembic,
    validar_historial_esquema,
)
from app.db.base import Base


TABLAS_ESPERADAS = set(Base.metadata.tables)


def _connection(tablas: set[str]):
    connection = Mock()
    inspector = Mock()
    inspector.get_table_names.return_value = sorted(tablas)
    inspector.has_table.return_value = False
    return connection, inspector


def test_sin_variable_stamp_de_base_existente_falla_con_guia():
    connection, inspector = _connection(TABLAS_ESPERADAS)

    with patch("app.db.alembic_safety.inspect", return_value=inspector):
        with pytest.raises(RuntimeError) as error:
            validar_historial_esquema(
                connection,
                tablas_esperadas=TABLAS_ESPERADAS,
                comando="stamp",
                permitir_adopcion=False,
            )

    assert "ALEMBIC_ALLOW_ADOPT_EXISTING=1" in str(error.value)
    assert GUIA_ADOPCION in str(error.value)


def test_stamp_con_variable_permite_esquema_completo():
    connection, inspector = _connection(TABLAS_ESPERADAS)

    with patch("app.db.alembic_safety.inspect", return_value=inspector):
        validar_historial_esquema(
            connection,
            tablas_esperadas=TABLAS_ESPERADAS,
            comando="stamp",
            permitir_adopcion=True,
        )


def test_stamp_no_adopta_una_base_vacia():
    connection, inspector = _connection(set())

    with patch("app.db.alembic_safety.inspect", return_value=inspector):
        with pytest.raises(RuntimeError, match="base vacía"):
            validar_historial_esquema(
                connection,
                tablas_esperadas=TABLAS_ESPERADAS,
                comando="stamp",
                permitir_adopcion=True,
            )


def test_upgrade_con_variable_sigue_rechazando_base_sin_historial():
    connection, inspector = _connection(TABLAS_ESPERADAS)

    with patch("app.db.alembic_safety.inspect", return_value=inspector):
        with pytest.raises(RuntimeError, match="ALEMBIC_ALLOW_ADOPT_EXISTING=1"):
            validar_historial_esquema(
                connection,
                tablas_esperadas=TABLAS_ESPERADAS,
                comando="upgrade",
                permitir_adopcion=True,
            )


def test_stamp_aborta_si_falta_una_tabla_esperada():
    tablas = set(TABLAS_ESPERADAS)
    tabla_faltante = sorted(tablas)[0]
    tablas.remove(tabla_faltante)
    connection, inspector = _connection(tablas)

    with patch("app.db.alembic_safety.inspect", return_value=inspector):
        with pytest.raises(RuntimeError, match=tabla_faltante):
            validar_historial_esquema(
                connection,
                tablas_esperadas=TABLAS_ESPERADAS,
                comando="stamp",
                permitir_adopcion=True,
            )


def test_comando_cli_stamp_se_identifica_por_nombre():
    def stamp(*_args):
        return None

    config = SimpleNamespace(cmd_opts=SimpleNamespace(cmd=(stamp, [], [])))

    assert obtener_comando_alembic(config) == "stamp"
