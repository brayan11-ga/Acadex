import secrets

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioUpdate
from app.services.usuario_service import (
    actualizar_usuario,
    hash_password,
    login,
    verify_password,
)


def test_actualizar_contrasena_guarda_hash_y_permite_login():
    anterior = secrets.token_urlsafe(18)
    nueva = secrets.token_urlsafe(18)
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Usuario.__table__.create(engine)

    try:
        with Session(engine) as db:
            usuario = Usuario(
                correo_electronico="admin@example.test",
                contrasena=hash_password(anterior),
                es_admin=True,
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)

            actualizado = actualizar_usuario(
                db,
                usuario.id_usuario,
                UsuarioUpdate(contrasena=nueva),
            )

            assert actualizado.contrasena != nueva
            assert verify_password(nueva, actualizado.contrasena)
            assert login(db, usuario.correo_electronico, nueva)
    finally:
        engine.dispose()
