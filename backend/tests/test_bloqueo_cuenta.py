import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.services import usuario_service


class BloqueoTemporalCuentaTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Usuario.__table__.create(self.engine)
        self.db = Session(self.engine)
        self.usuario = Usuario(
            correo_electronico="estudiante@example.test",
            contrasena="hash-sintetico",
            intentos_fallidos=0,
            bloqueado=False,
        )
        self.db.add(self.usuario)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_quinto_fallo_bloquea_quince_minutos_y_no_deja_bloqueo_permanente(self):
        with patch.object(usuario_service, "verify_password", return_value=False):
            for intento in range(1, 5):
                with self.subTest(intento=intento), self.assertRaises(HTTPException) as error:
                    usuario_service.login(
                        self.db, "estudiante@example.test", "incorrecta"
                    )
                self.assertEqual(error.exception.status_code, 401)

            with self.assertRaises(HTTPException) as error:
                usuario_service.login(
                    self.db, "estudiante@example.test", "incorrecta"
                )

        self.assertEqual(error.exception.status_code, 423)
        self.assertEqual(error.exception.headers["Retry-After"], "900")
        self.db.refresh(self.usuario)
        self.assertTrue(self.usuario.bloqueado)
        self.assertEqual(self.usuario.intentos_fallidos, 5)
        self.assertGreater(self.usuario.bloqueado_hasta, datetime.now(timezone.utc).replace(tzinfo=None))

    def test_bloqueo_permanente_heredado_sin_vencimiento_se_libera(self):
        self.usuario.bloqueado = True
        self.usuario.intentos_fallidos = 3
        self.db.commit()

        with patch.object(usuario_service, "verify_password", return_value=False):
            with self.assertRaises(HTTPException) as error:
                usuario_service.login(
                    self.db, "estudiante@example.test", "incorrecta"
                )

        self.assertEqual(error.exception.status_code, 401)
        self.db.refresh(self.usuario)
        self.assertFalse(self.usuario.bloqueado)
        self.assertIsNone(self.usuario.bloqueado_hasta)
        self.assertEqual(self.usuario.intentos_fallidos, 1)


if __name__ == "__main__":
    unittest.main()
