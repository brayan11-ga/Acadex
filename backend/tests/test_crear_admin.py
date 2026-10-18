import secrets

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.perfil import Perfil
from app.models.usuario import Usuario
from app.services.usuario_service import hash_password, verify_password
from scripts import crear_admin


@pytest.fixture
def sqlite_engine(tmp_path):
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'crear-admin.sqlite'}")
    Usuario.__table__.create(engine)
    Perfil.__table__.create(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db(sqlite_engine):
    with Session(sqlite_engine) as session:
        yield session


def test_crea_admin_con_hash_y_perfil(db):
    contrasena = secrets.token_urlsafe(18)

    estado = crear_admin.crear_o_promover_administrador(
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


def test_promueve_usuario_existente_sin_cambiar_contrasena(db):
    contrasena_anterior = secrets.token_urlsafe(18)
    usuario = Usuario(
        correo_electronico="persona@example.com",
        contrasena=hash_password(contrasena_anterior),
        es_admin=False,
    )
    db.add(usuario)
    db.commit()
    hash_anterior = usuario.contrasena

    estado = crear_admin.crear_o_promover_administrador(
        db,
        usuario.correo_electronico,
    )
    db.refresh(usuario)

    assert estado == "promovido"
    assert usuario.es_admin is True
    assert usuario.contrasena == hash_anterior
    assert verify_password(contrasena_anterior, usuario.contrasena)


def test_cli_no_reemplaza_password_del_entorno_sin_opcion_explicita(
    db,
    sqlite_engine,
    monkeypatch,
    capsys,
    caplog,
):
    usuario = Usuario(
        correo_electronico="persona@example.com",
        contrasena=hash_password(secrets.token_urlsafe(18)),
        es_admin=False,
    )
    db.add(usuario)
    db.commit()
    hash_anterior = usuario.contrasena
    contrasena_solicitada = secrets.token_urlsafe(18)

    monkeypatch.setattr(crear_admin, "engine", sqlite_engine)
    monkeypatch.setenv("ACADEX_ADMIN_EMAIL", usuario.correo_electronico)
    monkeypatch.setenv("ACADEX_ADMIN_PASSWORD", contrasena_solicitada)
    monkeypatch.setenv("ACADEX_ADMIN_PASSWORD_CONFIRM", contrasena_solicitada)

    assert crear_admin.main([]) == 0

    db.refresh(usuario)
    salida = capsys.readouterr()
    assert usuario.es_admin is True
    assert usuario.contrasena == hash_anterior
    assert contrasena_solicitada not in salida.out + salida.err + caplog.text


def test_reset_password_exige_confirmacion_y_no_imprime_ni_registra_contrasena(
    db,
    sqlite_engine,
    monkeypatch,
    capsys,
    caplog,
):
    usuario = Usuario(
        correo_electronico="persona@example.com",
        contrasena=hash_password(secrets.token_urlsafe(18)),
        es_admin=False,
    )
    db.add(usuario)
    db.commit()
    hash_anterior = usuario.contrasena
    contrasena_nueva = secrets.token_urlsafe(18)

    monkeypatch.setattr(crear_admin, "engine", sqlite_engine)
    monkeypatch.setenv("ACADEX_ADMIN_EMAIL", usuario.correo_electronico)
    monkeypatch.setenv("ACADEX_ADMIN_PASSWORD", contrasena_nueva)
    monkeypatch.setenv("ACADEX_ADMIN_PASSWORD_CONFIRM", secrets.token_urlsafe(18))

    assert crear_admin.main(["--reset-password"]) == 2
    db.refresh(usuario)
    assert usuario.contrasena == hash_anterior

    monkeypatch.setenv("ACADEX_ADMIN_PASSWORD_CONFIRM", contrasena_nueva)
    assert crear_admin.main(["--reset-password"]) == 0
    db.refresh(usuario)

    salida = capsys.readouterr()
    assert usuario.es_admin is True
    assert usuario.contrasena != hash_anterior
    assert verify_password(contrasena_nueva, usuario.contrasena)
    assert contrasena_nueva not in salida.out + salida.err + caplog.text


def test_variables_de_entorno_requieren_contrasena_y_confirmacion():
    with pytest.raises(ValueError, match="juntas"):
        crear_admin.obtener_contrasena(
            {
                "ACADEX_ADMIN_PASSWORD": secrets.token_urlsafe(18),
            }
        )


def test_contrasena_interactiva_se_confirma_sin_mostrarla():
    contrasena = secrets.token_urlsafe(18)
    secretos = iter([contrasena, contrasena])

    resultado = crear_admin.obtener_contrasena(
        {},
        leer_secreto=lambda _mensaje: next(secretos),
    )

    assert resultado == contrasena
