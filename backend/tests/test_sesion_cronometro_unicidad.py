import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.sesion_cronometro import SesionCronometro
from app.services import sesion_cronometro_service


class UnicidadSesionActivaTests(unittest.TestCase):
    def test_indice_parcial_impide_dos_sesiones_activas_para_la_misma_tarea(self):
        engine = create_engine("sqlite+pysqlite:///:memory:")
        SesionCronometro.__table__.create(engine)
        try:
            with Session(engine) as db:
                db.add(SesionCronometro(
                    fecha_inicio=datetime(2026, 10, 12, 10),
                    id_tarea=4,
                    id_usuario=8,
                ))
                db.commit()
                db.add(SesionCronometro(
                    fecha_inicio=datetime(2026, 10, 12, 11),
                    id_tarea=4,
                    id_usuario=9,
                ))
                with self.assertRaises(IntegrityError):
                    db.commit()
                db.rollback()
        finally:
            engine.dispose()

    def test_conflicto_concurrente_se_convierte_en_respuesta_normal(self):
        db = Mock()
        tarea = SimpleNamespace(verificar_permiso_tarea=Mock())
        conflicto = IntegrityError("insert", {}, RuntimeError("unique index"))

        with (
            patch.object(sesion_cronometro_service, "tarea_service", tarea),
            patch.object(sesion_cronometro_service.repo, "get_sesion_activa", return_value=None),
            patch.object(sesion_cronometro_service.repo, "create_sesion", side_effect=conflicto),
        ):
            with self.assertRaises(HTTPException) as error:
                sesion_cronometro_service.iniciar_sesion(db, 9, 4)

        self.assertEqual(error.exception.status_code, 409)
        db.rollback.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
