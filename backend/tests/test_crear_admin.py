import secrets

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.perfil import Perfil
from app.models.usuario import Usuario
from scripts.crear_admin import (
    crear_o_promover_administrador,
    obtener_credenciales,
)
from app.services.usuario_service import hash_password, verify_password


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Usuario.__table__.create(engine)
    Perfil.__table__.create(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_crea_admin_con_hash_y_perfil(db):
    contrasena = secrets.token_urlsafe(18)

    estado = crear_o_promover_administrador(
        db,
        "admin@example.com",
        contrasena,
    )
    usuario = db.query(Usuario).filter_by(correo_electronico="admin@example.com").one()
    perfil = db.query(Perfil).filter_by(id_usuario=usuario.id_usuario).one()

    assert estado == "creado"
    assert usuario.es_admin is True
    assert usuario.contrasena != contrasena
    assert verify_password(contrasena, usuario.contrasena)
    assert perfil.nombre_usuario == "admin"


def test_promueve_usuario_existente_y_actualiza_hash(db):
    contrasena_anterior = secrets.token_urlsafe(18)
    contrasena_nueva = secrets.token_urlsafe(18)
    usuario = Usuario(
        correo_electronico="persona@example.com",
        contrasena=hash_password(contrasena_anterior),
        es_admin=False,
    )
    db.add(usuario)
    db.commit()

    estado = crear_o_promover_administrador(
        db,
        usuario.correo_electronico,
        contrasena_nueva,
    )
    db.refresh(usuario)

    assert estado == "promovido"
    assert usuario.es_admin is True
    assert usuario.contrasena != contrasena_nueva
    assert verify_password(contrasena_nueva, usuario.contrasena)


def test_credenciales_por_entorno_requieren_ambas_variables():
    with pytest.raises(ValueError, match="juntas"):
        obtener_credenciales({"ACADEX_ADMIN_EMAIL": "admin@example.com"})


def test_credenciales_interactivas_confirman_sin_revelar_contrasena():
    entradas = iter(["admin@example.com"])
    secretos = iter([secrets.token_urlsafe(18)] * 2)

    correo, contrasena = obtener_credenciales(
        {},
        leer=lambda _mensaje: next(entradas),
        leer_secreto=lambda _mensaje: next(secretos),
    )

    assert correo == "admin@example.com"
    assert len(contrasena) >= 8
