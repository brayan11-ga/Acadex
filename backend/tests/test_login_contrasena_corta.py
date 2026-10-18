import secrets

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest
from app.services.usuario_service import hash_password, login


def test_login_permite_contrasena_existente_menor_de_ocho_caracteres():
    contrasena_corta = secrets.token_hex(2)
    credenciales = LoginRequest(
        correo_electronico="estudiante@example.com",
        contrasena=contrasena_corta,
    )
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Usuario.__table__.create(engine)

    try:
        with Session(engine) as db:
            db.add(
                Usuario(
                    correo_electronico=credenciales.correo_electronico,
                    contrasena=hash_password(contrasena_corta),
                )
            )
            db.commit()

            token = login(
                db,
                credenciales.correo_electronico,
                credenciales.contrasena,
            )

            assert len(contrasena_corta) < 8
            assert token
    finally:
        engine.dispose()
