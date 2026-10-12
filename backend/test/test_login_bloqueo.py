import pytest
from fastapi import HTTPException
from app.services import usuario_service as service


CORREO = "bloqueo_test@email.com"
PASSWORD_CORRECTA = "Password123"
PASSWORD_INCORRECTA = "ClaveIncorrecta"


@pytest.fixture()
def usuario_registrado(db_session):
    """Registra un usuario de prueba antes de cada test de este archivo."""
    service.registrar_usuario(db_session, CORREO, PASSWORD_CORRECTA)
    return CORREO


class TestBloqueoPorIntentosFallidos:

    def test_cuenta_se_bloquea_tras_tres_intentos_fallidos(self, db_session, usuario_registrado):
        # 3 intentos fallidos consecutivos
        for _ in range(3):
            with pytest.raises(HTTPException) as exc:
                service.login(db_session, usuario_registrado, PASSWORD_INCORRECTA)
            assert exc.value.status_code == 401

        # El 4to intento, incluso con la contraseña CORRECTA, debe fallar porque la cuenta quedó bloqueada
        with pytest.raises(HTTPException) as exc:
            service.login(db_session, usuario_registrado, PASSWORD_CORRECTA)

        assert exc.value.status_code == 423
        assert "bloqueada" in exc.value.detail.lower()

    def test_login_exitoso_reinicia_contador_de_intentos_fallidos(self, db_session, usuario_registrado):
        # 2 intentos fallidos (no llega al límite de 3)
        for _ in range(2):
            with pytest.raises(HTTPException):
                service.login(db_session, usuario_registrado, PASSWORD_INCORRECTA)

        # Login correcto debe funcionar y reiniciar el contador
        token = service.login(db_session, usuario_registrado, PASSWORD_CORRECTA)
        assert token is not None

        from app.repositories import usuario_repository as repo
        usuario = repo.get_usuario_by_correo(db_session, usuario_registrado)
        assert usuario.intentos_fallidos == 0
        assert usuario.bloqueado is False