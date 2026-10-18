"""Validación y guardas de las pruebas PostgreSQL.

La validación de configuración es pura: no carga settings de la aplicación,
no importa SQLAlchemy y no realiza operaciones de red. El acceso a PostgreSQL
solo se habilita desde un runner Compose aislado identificado operativamente.
"""

import re
from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import dataclass, field


TEST_DATABASE_NAME = "acadex_test"
TEST_RUNNER_CONTEXT = "isolated-compose"
TEST_RUNNER_MARKER_PATH = "/run/secrets/acadex-test-runner"
_SCHEMA_NAME = re.compile(r"acadex_test_[0-9a-f]{32}\Z")
_COMPOSE_PROJECT_NAME = re.compile(r"acadex-test-[a-f0-9]{8,32}\Z")


class UnsafeTestDatabaseError(RuntimeError):
    """La configuración no demuestra que el destino sea una BD desechable."""


@dataclass(frozen=True)
class TestDatabaseConfig:
    """Configuración exclusiva de pruebas, sin depender de Settings de producción."""

    database: str
    host: str
    port: int
    target: str
    compose_project: str
    username: str = field(repr=False)
    password: str = field(repr=False)

    def backend_environment(self) -> dict[str, str]:
        """Proyecta explícitamente el destino validado para imports del backend."""
        return {
            "APP_ENV": "test",
            "DB_USER": self.username,
            "DB_PASSWORD": self.password,
            "DB_HOST": self.host,
            "DB_PORT": str(self.port),
            "DB_NAME": self.database,
            "DB_SSLMODE": "disable",
            "DB_SSLROOTCERT": "",
        }


def validar_configuracion_pruebas(
    environment: Mapping[str, str],
) -> TestDatabaseConfig:
    """Valida variables test-only sin cargar configuración ni contactar servicios."""
    if environment.get("ACADEX_RUN_POSTGRES_TESTS") != "1":
        raise UnsafeTestDatabaseError(
            "Pruebas PostgreSQL bloqueadas: define ACADEX_RUN_POSTGRES_TESTS=1."
        )

    required = (
        "ACADEX_TEST_DB_NAME",
        "ACADEX_TEST_DB_TARGET",
        "ACADEX_TEST_DB_HOST",
        "ACADEX_TEST_DB_PORT",
        "ACADEX_TEST_DB_USER",
        "ACADEX_TEST_DB_PASSWORD",
        "ACADEX_TEST_COMPOSE_PROJECT",
    )
    missing = [name for name in required if not environment.get(name, "").strip()]
    if missing:
        raise UnsafeTestDatabaseError(
            "Configuración de pruebas incompleta; faltan: " + ", ".join(missing)
        )

    database = environment["ACADEX_TEST_DB_NAME"].strip()
    target = environment["ACADEX_TEST_DB_TARGET"].strip()
    host = environment["ACADEX_TEST_DB_HOST"].strip()
    raw_port = environment["ACADEX_TEST_DB_PORT"].strip()
    project = environment["ACADEX_TEST_COMPOSE_PROJECT"].strip()
    runtime_project = environment.get("COMPOSE_PROJECT_NAME", "").strip()
    username = environment["ACADEX_TEST_DB_USER"].strip()
    password = environment["ACADEX_TEST_DB_PASSWORD"]

    if database != TEST_DATABASE_NAME:
        raise UnsafeTestDatabaseError(
            f"ACADEX_TEST_DB_NAME debe ser exactamente {TEST_DATABASE_NAME}."
        )
    if target != "compose" or host != "db" or raw_port != "5432":
        raise UnsafeTestDatabaseError(
            "Las pruebas PostgreSQL solo admiten target=compose, host=db y puerto=5432."
        )
    if not _COMPOSE_PROJECT_NAME.fullmatch(project):
        raise UnsafeTestDatabaseError(
            "ACADEX_TEST_COMPOSE_PROJECT debe identificar un proyecto acadex-test aislado."
        )
    if runtime_project != project:
        raise UnsafeTestDatabaseError(
            "COMPOSE_PROJECT_NAME debe coincidir con ACADEX_TEST_COMPOSE_PROJECT."
        )
    if not username or not password.strip():
        raise UnsafeTestDatabaseError(
            "Las credenciales ACADEX_TEST_DB_USER y ACADEX_TEST_DB_PASSWORD son obligatorias."
        )

    expected_normal_values = {
        "DB_USER": username,
        "DB_PASSWORD": password,
        "DB_HOST": host,
        "DB_PORT": raw_port,
        "DB_NAME": database,
        "DB_SSLMODE": "disable",
        "DB_SSLROOTCERT": "",
    }
    for name, expected in expected_normal_values.items():
        configured = environment.get(name)
        if configured is not None:
            actual = configured if name == "DB_PASSWORD" else configured.strip()
            if actual != expected:
                raise UnsafeTestDatabaseError(
                    f"{name} contradice la configuración explícita ACADEX_TEST_*."
                )

    # libpq admite destinos alternativos por variables de entorno. Aunque la URL
    # explícita debe prevalecer, aceptarlas haría ambiguo el contrato de pruebas.
    for name in (
        "DATABASE_URL",
        "DATABASES_URL",
        "PGHOST",
        "PGHOSTADDR",
        "PGPORT",
        "PGDATABASE",
        "PGUSER",
        "PGPASSWORD",
        "PGSERVICE",
        "PGSERVICEFILE",
    ):
        if environment.get(name, "").strip():
            raise UnsafeTestDatabaseError(
                f"{name} no se admite en el entorno de pruebas PostgreSQL."
            )

    return TestDatabaseConfig(
        database=database,
        host=host,
        port=5432,
        target=target,
        compose_project=project,
        username=username,
        password=password,
    )


def validar_runner_compose_aislado(
    environment: Mapping[str, str],
    *,
    en_contenedor: bool,
    marcador_aislamiento_presente: bool,
) -> None:
    """Exige evidencias operativas que el Compose actual todavía no proporciona."""
    if (
        environment.get("ACADEX_TEST_RUNNER_CONTEXT") != TEST_RUNNER_CONTEXT
        or not en_contenedor
        or not marcador_aislamiento_presente
    ):
        raise UnsafeTestDatabaseError(
            "Pruebas PostgreSQL bloqueadas: falta el runner Compose aislado y su "
            "marcador operativo en /run/secrets/acadex-test-runner."
        )


def proyectar_configuracion_pruebas_backend(
    config: TestDatabaseConfig,
    environment: MutableMapping[str, str],
) -> None:
    """Hace explícito que cualquier sesión global importada apunta a la BD de prueba."""
    environment.update(config.backend_environment())


def crear_engine_pruebas(
    environment: Mapping[str, str],
    engine_factory: Callable[[TestDatabaseConfig], object],
    *,
    en_contenedor: bool,
    marcador_aislamiento_presente: bool,
) -> object:
    """Valida configuración y runner antes de invocar la fábrica de engines."""
    config = validar_configuracion_pruebas(environment)
    validar_runner_compose_aislado(
        environment,
        en_contenedor=en_contenedor,
        marcador_aislamiento_presente=marcador_aislamiento_presente,
    )
    return engine_factory(config)


def validar_destino_pruebas(
    *,
    configured_database: str,
    actual_database: str,
    expected_database: str | None,
    run_postgres_tests: str | None,
) -> None:
    """Comprobación secundaria del nombre informado por PostgreSQL tras conectar."""
    if run_postgres_tests != "1":
        raise UnsafeTestDatabaseError(
            "Pruebas PostgreSQL bloqueadas: define ACADEX_RUN_POSTGRES_TESTS=1."
        )
    if expected_database != TEST_DATABASE_NAME:
        raise UnsafeTestDatabaseError(
            f"Pruebas PostgreSQL bloqueadas: ACADEX_TEST_DB_NAME debe ser "
            f"{TEST_DATABASE_NAME}."
        )
    if configured_database != TEST_DATABASE_NAME:
        raise UnsafeTestDatabaseError(
            f"Pruebas PostgreSQL bloqueadas: DB_NAME debe ser {TEST_DATABASE_NAME}."
        )
    if actual_database != TEST_DATABASE_NAME:
        raise UnsafeTestDatabaseError(
            "Pruebas PostgreSQL bloqueadas: PostgreSQL informó una base distinta "
            f"de {TEST_DATABASE_NAME}."
        )


def _validar_esquema(schema_name: str) -> None:
    if not _SCHEMA_NAME.fullmatch(schema_name):
        raise UnsafeTestDatabaseError("Nombre de esquema de pruebas no autorizado.")


def crear_esquema_pruebas(
    engine,
    schema_name: str,
    *,
    configured_database: str,
    expected_database: str | None,
    run_postgres_tests: str | None,
) -> None:
    """Verifica el nombre real antes de crear un esquema aleatorio.

    El llamador debe validar la configuración y el runner antes de construir el
    engine. Esta comprobación del servidor es una segunda barrera, posterior a
    la conexión.
    """
    _validar_esquema(schema_name)
    from sqlalchemy import text

    with engine.connect() as connection:
        actual_database = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()
    validar_destino_pruebas(
        configured_database=configured_database,
        actual_database=actual_database,
        expected_database=expected_database,
        run_postgres_tests=run_postgres_tests,
    )

    # El identificador ya fue validado contra una expresión estricta; no
    # acepta comillas ni SQL arbitrario.
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema_name}"'))


def eliminar_esquema_pruebas(
    engine,
    schema_name: str,
    *,
    configured_database: str,
    expected_database: str | None,
    run_postgres_tests: str | None,
) -> None:
    """Elimina exclusivamente el esquema aleatorio de esta ejecución."""
    _validar_esquema(schema_name)
    from sqlalchemy import text

    with engine.connect() as connection:
        actual_database = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()
    validar_destino_pruebas(
        configured_database=configured_database,
        actual_database=actual_database,
        expected_database=expected_database,
        run_postgres_tests=run_postgres_tests,
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA "{schema_name}" CASCADE'))
