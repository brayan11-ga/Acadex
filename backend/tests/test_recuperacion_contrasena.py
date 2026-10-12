import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLSession

from app.api.v1.endpoints import usuarios as usuarios_endpoint
from app.db.base import Base
from app.models.grupo import Grupo
from app.models.token_temporal import TokenTemporal
from app.models.usuario import Usuario
from app.schemas.auth import ForgotPasswordIn
from app.services import usuario_service


def ahora_utc_sin_zona():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RecuperacionContrasenaTests(unittest.TestCase):
    def test_endpoint_de_forgot_devuelve_no_disponible_si_no_hay_configuracion(self):
        db = Mock()
        with (
            patch.object(usuarios_endpoint, "settings", SimpleNamespace(password_reset_enabled=False)),
            patch.object(usuarios_endpoint.service, "solicitar_reset_por_correo") as solicitar,
        ):
            with self.assertRaises(HTTPException) as error:
                usuarios_endpoint.forgot_password(
                    ForgotPasswordIn(correo_electronico="persona@example.com"), db
                )

        self.assertEqual(error.exception.status_code, 503)
        solicitar.assert_not_called()

    def test_fallo_smtp_invalida_token_y_no_revela_si_el_correo_existe(self):
        db = Mock()
        token = SimpleNamespace(valor_token="digest-sintetico", usado=False)
        with (
            patch.object(usuarios_endpoint, "settings", SimpleNamespace(password_reset_enabled=True)),
            patch.object(usuarios_endpoint.service, "solicitar_reset_por_correo", return_value=(token, "token-una-sola-vez")),
            patch.object(usuarios_endpoint, "enviar_reset", side_effect=OSError("SMTP no disponible")),
            patch.object(usuarios_endpoint.service, "invalidar_token_reset") as invalidar,
            self.assertLogs("app.api.v1.endpoints.usuarios", level="ERROR"),
        ):
            respuesta = usuarios_endpoint.forgot_password(
                ForgotPasswordIn(correo_electronico="persona@example.com"), db
            )

        invalidar.assert_called_once_with(db, token)
        self.assertEqual(respuesta, {"mensaje": "Si el correo existe, recibirás un enlace"})

    def test_correo_desconocido_no_crea_token(self):
        db = Mock()
        with patch.object(usuario_service.repo, "get_usuario_by_correo", return_value=None):
            resultado = usuario_service.solicitar_reset_por_correo(db, "nadie@example.test")

        self.assertIsNone(resultado)
        db.add.assert_not_called()
        db.commit.assert_not_called()

    def test_solicitud_invalida_tokens_anteriores_y_crea_token_corto(self):
        db = Mock()
        usuario = SimpleNamespace(id_usuario=41)
        with (
            patch.object(usuario_service.repo, "get_usuario_by_correo", return_value=usuario),
            patch.object(usuario_service.secrets, "token_urlsafe", return_value="token-sintetico"),
        ):
            token, valor_token = usuario_service.solicitar_reset_por_correo(
                db, "persona@example.test"
            )

        db.query.assert_called_with(TokenTemporal)
        db.query.return_value.filter.return_value.update.assert_called_once_with(
            {"usado": True}, synchronize_session=False
        )
        self.assertEqual(token.id_usuario, 41)
        self.assertEqual(token.tipo_token, "reset_password")
        self.assertEqual(valor_token, "token-sintetico")
        self.assertEqual(token.valor_token, usuario_service._hash_token_reset(valor_token))
        self.assertLessEqual(len(token.valor_token), 50)
        self.assertFalse(token.usado)
        db.commit.assert_called_once_with()

    def test_token_expirado_o_usado_no_cambia_contrasena(self):
        for usado, vencimiento in (
            (False, ahora_utc_sin_zona() - timedelta(minutes=1)),
            (True, ahora_utc_sin_zona() + timedelta(minutes=1)),
        ):
            with self.subTest(usado=usado):
                db = Mock()
                token = SimpleNamespace(
                    id_token=1,
                    id_usuario=41,
                    usado=usado,
                    fecha_expiracion=vencimiento,
                )
                db.query.return_value.filter.return_value.first.return_value = token

                with (
                    patch.object(usuario_service.repo, "get_usuario_by_id") as buscar,
                    patch.object(usuario_service, "hash_password") as hash_password,
                ):
                    with self.assertRaises(HTTPException) as error:
                        usuario_service.restablecer_password_con_token(db, "token", "NuevaClave123")

                self.assertEqual(error.exception.status_code, 400)
                buscar.assert_not_called()
                hash_password.assert_not_called()
                db.commit.assert_not_called()

    def test_token_valido_se_reclama_y_contrasena_se_confirma(self):
        db = Mock()
        token = SimpleNamespace(
            id_token=5,
            id_usuario=41,
            usado=False,
            fecha_expiracion=ahora_utc_sin_zona() + timedelta(minutes=5),
        )
        usuario = SimpleNamespace(id_usuario=41, contrasena="hash-anterior")
        db.query.return_value.filter.return_value.first.return_value = token
        db.query.return_value.filter.return_value.update.return_value = 1

        with (
            patch.object(usuario_service.repo, "get_usuario_by_id", return_value=usuario),
            patch.object(usuario_service, "hash_password", return_value="hash-nuevo") as hash_password,
        ):
            resultado = usuario_service.restablecer_password_con_token(db, "token", "NuevaClave123")

        self.assertIsNone(resultado)
        self.assertEqual(usuario.contrasena, "hash-nuevo")
        hash_password.assert_called_once_with("NuevaClave123")
        self.assertEqual(db.query.return_value.filter.return_value.update.call_count, 2)
        db.commit.assert_called_once_with()
        db.rollback.assert_not_called()

    def test_dos_usos_concurrentes_no_confirman_el_segundo_cambio(self):
        db = Mock()
        token = SimpleNamespace(
            id_token=5,
            id_usuario=41,
            usado=False,
            fecha_expiracion=ahora_utc_sin_zona() + timedelta(minutes=5),
        )
        usuario = SimpleNamespace(id_usuario=41, contrasena="hash-anterior")
        db.query.return_value.filter.return_value.first.return_value = token
        db.query.return_value.filter.return_value.update.return_value = 0

        with (
            patch.object(usuario_service.repo, "get_usuario_by_id", return_value=usuario),
            patch.object(usuario_service, "hash_password") as hash_password,
        ):
            with self.assertRaises(HTTPException) as error:
                usuario_service.restablecer_password_con_token(db, "token", "NuevaClave123")

        self.assertEqual(error.exception.status_code, 400)
        hash_password.assert_not_called()
        db.commit.assert_not_called()
        db.rollback.assert_called_once_with()

    def test_reset_completo_persiste_digest_y_rechaza_reutilizacion_en_sqlite(self):
        engine = create_engine("sqlite:///:memory:")
        tablas = [Usuario.__table__, Grupo.__table__, TokenTemporal.__table__]
        Base.metadata.create_all(engine, tables=tablas)
        try:
            with SQLSession(engine) as db:
                usuario = Usuario(
                    correo_electronico="persona@example.com",
                    contrasena="hash-anterior",
                    es_admin=False,
                )
                db.add(usuario)
                db.commit()
                db.refresh(usuario)

                token_row, token_raw = usuario_service.generar_token_reset_password(
                    db, usuario.id_usuario
                )
                self.assertNotEqual(token_row.valor_token, token_raw)
                self.assertEqual(
                    db.query(TokenTemporal).filter_by(id_token=token_row.id_token).one().valor_token,
                    usuario_service._hash_token_reset(token_raw),
                )

                with patch.object(usuario_service, "hash_password", return_value="hash-nuevo"):
                    usuario_service.restablecer_password_con_token(
                        db, token_raw, "NuevaClave123"
                    )

                db.refresh(usuario)
                self.assertEqual(usuario.contrasena, "hash-nuevo")
                self.assertTrue(
                    db.query(TokenTemporal).filter_by(id_token=token_row.id_token).one().usado
                )
                with self.assertRaises(HTTPException) as error:
                    usuario_service.restablecer_password_con_token(
                        db, token_raw, "OtraClave123"
                    )
                self.assertEqual(error.exception.status_code, 400)
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
