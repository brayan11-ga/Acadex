import os
import uuid
from pathlib import Path

import pytest

from app.testing.postgres_safety import (
    TEST_RUNNER_MARKER_PATH,
    crear_engine_pruebas,
    crear_esquema_pruebas,
    eliminar_esquema_pruebas,
    proyectar_configuracion_pruebas_backend,
    validar_configuracion_pruebas,
    validar_runner_compose_aislado,
)


@pytest.fixture(scope="session", autouse=True)
def postgres_resources():
    """Valida primero; después prepara la aplicación y el PostgreSQL aislado."""
    if os.getenv("ACADEX_RUN_POSTGRES_TESTS") != "1":
        pytest.skip("Pruebas PostgreSQL deshabilitadas; el opt-in no está activo.")

    test_config = validar_configuracion_pruebas(os.environ)
    en_contenedor = Path("/.dockerenv").is_file()
    marcador_presente = Path(TEST_RUNNER_MARKER_PATH).is_file()
    validar_runner_compose_aislado(
        os.environ,
        en_contenedor=en_contenedor,
        marcador_aislamiento_presente=marcador_presente,
    )
    proyectar_configuracion_pruebas_backend(test_config, os.environ)

    # Los imports de la aplicación pueden construir el engine global. Se hacen
    # solo después de validar el destino y el runner, con DB_* proyectadas desde
    # variables exclusivas de pruebas.
    from sqlalchemy import create_engine
    from sqlalchemy.engine import URL
    from sqlalchemy.orm import sessionmaker
    from fastapi.testclient import TestClient

    from app.db.base import Base
    from app.db.session import engine as backend_engine
    from app.dependencies.db import get_db
    from app.main import app

    import app.models  # noqa: F401 - registra todos los modelos en metadata

    test_schema_name = f"acadex_test_{uuid.uuid4().hex}"

    def engine_factory(config, **options):
        url = URL.create(
            "postgresql+psycopg2",
            username=config.username,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
        )
        return create_engine(url, **options)

    def crear_engine_test(**options):
        return crear_engine_pruebas(
            os.environ,
            lambda config: engine_factory(config, **options),
            en_contenedor=en_contenedor,
            marcador_aislamiento_presente=marcador_presente,
        )

    admin_engine = crear_engine_test(connect_args={"options": "-c lc_messages=C"})
    engine = crear_engine_test(
        connect_args={
            "options": f"-c search_path={test_schema_name} -c lc_messages=C"
        }
    )
    testing_session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    esquema_creado = False
    try:
        crear_esquema_pruebas(
            admin_engine,
            test_schema_name,
            configured_database=test_config.database,
            expected_database=test_config.database,
            run_postgres_tests=os.getenv("ACADEX_RUN_POSTGRES_TESTS"),
        )
        esquema_creado = True
        Base.metadata.create_all(bind=engine)
        yield {
            "engine": engine,
            "session_local": testing_session_local,
            "app": app,
            "get_db": get_db,
            "test_client": TestClient,
        }
    finally:
        engine.dispose()
        if esquema_creado:
            eliminar_esquema_pruebas(
                admin_engine,
                test_schema_name,
                configured_database=test_config.database,
                expected_database=test_config.database,
                run_postgres_tests=os.getenv("ACADEX_RUN_POSTGRES_TESTS"),
            )
        admin_engine.dispose()
        backend_engine.dispose()


@pytest.fixture()
def db_session(postgres_resources):
    """Sesión de BD con rollback automático al final de cada test, para que no queden datos entre pruebas."""
    connection = postgres_resources["engine"].connect()
    transaction = connection.begin()
    session = postgres_resources["session_local"](bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session, postgres_resources):
    """TestClient de FastAPI usando la sesión de BD de prueba en lugar de la real."""
    def override_get_db():
        yield db_session

    app = postgres_resources["app"]
    get_db = postgres_resources["get_db"]
    app.dependency_overrides[get_db] = override_get_db
    with postgres_resources["test_client"](app) as c:
        yield c
    app.dependency_overrides.clear()
