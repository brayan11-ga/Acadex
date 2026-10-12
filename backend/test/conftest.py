import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

os.environ["ENV_FILE"] = ".env.test"

from app.config.settings import Settings
from app.db.base import Base
from app.dependencies.db import get_db
from app.main import app

test_settings = Settings(_env_file=".env.test")

engine = create_engine(
    test_settings.database_url,
    connect_args={"options": "-c lc_messages=C"},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def crear_tablas():
    """Crea todas las tablas al iniciar la sesión de pruebas y las elimina al final."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Sesión de BD con rollback automático al final de cada test, para que no queden datos entre pruebas."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """TestClient de FastAPI usando la sesión de BD de prueba en lugar de la real."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()