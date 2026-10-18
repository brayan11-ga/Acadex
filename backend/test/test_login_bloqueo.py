import pytest
from fastapi import HTTPException


CORREO = "bloqueo_test@email.com"
PASSWORD_CORRECTA = "Password123"
PASSWORD_INCORRECTA = "ClaveIncorrecta"


@pytest.fixture()
def service(db_session):
    """Importa el servicio después de que el fixture haya protegido la BD."""
    from app.services import usuario_service

    return usuario_service


@pytest.fixture()
def usuario_registrado(db_session, service):
    """Registra un usuario de prueba antes de cada test de este archivo."""
    service.registrar_usuario(
        db_session,
        CORREO,
        PASSWORD_CORRECTA,
        acepta_tratamiento_datos=True,
        confirma_aviso_almacenamiento=True,
    )
    return CORREO


class TestBloqueoPorIntentosFallidos:

    def test_cuenta_se_bloquea_tras_cinco_intentos_fallidos(
        self, db_session, usuario_registrado, service
    ):
        # Los primeros 4 intentos fallidos no alcanzan el umbral del servicio.
        for _ in range(4):
            with pytest.raises(HTTPException) as exc:
                service.login(db_session, usuario_registrado, PASSWORD_INCORRECTA)
            assert exc.value.status_code == 401

        # El 5to intento activa el bloqueo.
        with pytest.raises(HTTPException) as exc:
            service.login(db_session, usuario_registrado, PASSWORD_INCORRECTA)

        assert exc.value.status_code == 423
        assert "bloqueada" in exc.value.detail.lower()

        # Mientras el bloqueo está vigente, tampoco se acepta la contraseña correcta.
        with pytest.raises(HTTPException) as exc:
            service.login(db_session, usuario_registrado, PASSWORD_CORRECTA)
        assert exc.value.status_code == 423

    def test_login_exitoso_reinicia_contador_de_intentos_fallidos(
        self, db_session, usuario_registrado, service
    ):
        # 2 intentos fallidos no alcanzan el umbral de 5.
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
