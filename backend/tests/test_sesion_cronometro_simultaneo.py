# Ruta: backend/tests/test_sesion_cronometro_simultaneo.py
"""Cronómetro simultáneo: una sesión activa por (tarea, usuario)."""

import unittest
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.sesion_cronometro import SesionCronometro
from app.repositories import sesion_cronometro_repository as repo
from app.services import sesion_cronometro_service


class CronometroSimultaneoTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        SesionCronometro.__table__.create(self.engine)
        self.db = Session(self.engine)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _iniciar(self, id_usuario: int, id_tarea: int = 4):
        with patch.object(
            sesion_cronometro_service.tarea_service, "verificar_permiso_tarea"
        ):
            return sesion_cronometro_service.iniciar_sesion(
                self.db, id_usuario, id_tarea
            )

    def test_dos_usuarios_inician_su_cronometro_en_la_misma_tarea(self):
        primera = self._iniciar(8)
        segunda = self._iniciar(9)
        self.assertEqual((primera.id_usuario, primera.id_tarea), (8, 4))
        self.assertEqual((segunda.id_usuario, segunda.id_tarea), (9, 4))

    def test_mismo_usuario_no_puede_iniciar_dos_veces(self):
        self._iniciar(8)
        with self.assertRaises(HTTPException) as error:
            self._iniciar(8)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(
            error.exception.detail,
            "Ya tienes una sesión activa en esta tarea",
        )

    def test_sesion_abierta_de_otro_usuario_no_bloquea_al_propio(self):
        self._iniciar(8)
        self.assertIsNotNone(repo.get_sesion_activa_de_usuario(self.db, 4, 8))
        self.assertIsNone(repo.get_sesion_activa_de_usuario(self.db, 4, 9))

    def test_finalizar_y_descartar_solo_afectan_la_sesion_propia(self):
        sesion_a = self._iniciar(8)
        sesion_b = self._iniciar(9)

        finalizada = sesion_cronometro_service.finalizar_sesion(
            self.db, sesion_a.id_sesion, 8
        )
        self.assertIsNotNone(finalizada.fecha_fin)

        with self.assertRaises(HTTPException) as error_finalizar:
            sesion_cronometro_service.finalizar_sesion(
                self.db, sesion_b.id_sesion, 8
            )
        self.assertEqual(error_finalizar.exception.status_code, 404)

        with self.assertRaises(HTTPException) as error_descartar:
            sesion_cronometro_service.descartar_sesion(
                self.db, sesion_b.id_sesion, 8
            )
        self.assertEqual(error_descartar.exception.status_code, 404)

        # La sesión del usuario 9 sigue abierta e intacta.
        self.assertIsNotNone(repo.get_sesion_activa_de_usuario(self.db, 4, 9))


if __name__ == "__main__":
    unittest.main()
