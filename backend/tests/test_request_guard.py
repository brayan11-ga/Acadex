import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.request_guard import limitar_solicitudes
from app.models.limite_solicitud import LimiteSolicitud


class LimiteSolicitudesTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        LimiteSolicitud.__table__.create(self.engine)
        self.db = Session(self.engine)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_limite_es_compartido_por_sesiones_y_devuelve_tiempo_de_espera(self):
        otra_sesion = Session(self.engine)
        try:
            argumentos = {
                "maximo": 2,
                "ventana_segundos": 60,
            }
            limitar_solicitudes(self.db, "login", "correo@example.test", **argumentos)
            limitar_solicitudes(otra_sesion, "login", "correo@example.test", **argumentos)

            with self.assertRaises(HTTPException) as error:
                limitar_solicitudes(self.db, "login", "correo@example.test", **argumentos)

            self.assertEqual(error.exception.status_code, 429)
            self.assertGreaterEqual(int(error.exception.headers["Retry-After"]), 1)
            fila = self.db.query(LimiteSolicitud).one()
            self.assertNotIn("correo@example.test", fila.clave_hash)
        finally:
            otra_sesion.close()

    def test_falla_cerrado_si_falta_la_migracion(self):
        LimiteSolicitud.__table__.drop(self.engine)

        with self.assertRaises(HTTPException) as error:
            limitar_solicitudes(
                self.db,
                "login",
                "ip-sintetica",
                maximo=5,
                ventana_segundos=60,
            )

        self.assertEqual(error.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
