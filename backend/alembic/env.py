"""Alembic usa el engine compartido por la aplicación FastAPI."""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import text

from app.config.settings import settings
from app.db.base import Base
from app.db.alembic_safety import (
    obtener_comando_alembic,
    validar_historial_esquema,
)
from app.db.session import engine
import app.models  # noqa: F401 - registra los 18 modelos en Base.metadata


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _incluir_objeto(objeto, nombre, tipo_objeto, reflejado, comparado) -> bool:
    """Alembic administra su tabla de control, no es parte de los modelos."""
    if tipo_objeto == "table" and nombre == "alembic_version":
        return False
    return True


def _validar_destino_de_pruebas(connection) -> None:
    """Impide que el runner de pruebas apunte a otra base o a otro Compose."""
    if settings.app_env != "test":
        return

    from app.testing.postgres_safety import (
        TEST_RUNNER_MARKER_PATH,
        validar_configuracion_pruebas,
        validar_destino_pruebas,
        validar_runner_compose_aislado,
    )

    config_pruebas = validar_configuracion_pruebas(os.environ)
    validar_runner_compose_aislado(
        os.environ,
        en_contenedor=os.path.isfile("/.dockerenv"),
        marcador_aislamiento_presente=os.path.isfile(TEST_RUNNER_MARKER_PATH),
    )
    base_actual = connection.execute(text("SELECT current_database()")).scalar_one()
    validar_destino_pruebas(
        configured_database=config_pruebas.database,
        actual_database=base_actual,
        expected_database=config_pruebas.database,
        run_postgres_tests=os.getenv("ACADEX_RUN_POSTGRES_TESTS"),
    )


def _rechazar_esquema_existente_sin_historial(connection) -> None:
    """No adopta a ciegas; permite solo stamp explícito de esquema completo."""
    validar_historial_esquema(
        connection,
        tablas_esperadas=set(target_metadata.tables),
        comando=obtener_comando_alembic(config),
        permitir_adopcion=os.getenv("ALEMBIC_ALLOW_ADOPT_EXISTING") == "1",
    )


def run_migrations_offline() -> None:
    """Genera SQL sin abrir una conexión a PostgreSQL."""
    context.configure(
        url=engine.url.render_as_string(hide_password=True),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema="public",
        compare_type=True,
        compare_server_default=True,
        include_object=_incluir_objeto,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta revisiones con el mismo engine que usa FastAPI."""
    with engine.connect() as connection:
        _validar_destino_de_pruebas(connection)
        _rechazar_esquema_existente_sin_historial(connection)
        # Las consultas de seguridad activan el autobegin de SQLAlchemy. Se
        # cierra esa transacción de solo lectura antes de que Alembic gestione
        # la transacción de DDL; de lo contrario el context manager externo
        # puede dejarla sin commit al cerrar la conexión.
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema="public",
            compare_type=True,
            compare_server_default=True,
            include_object=_incluir_objeto,
            transaction_per_migration=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
