# Ruta: backend/tests/test_descartar_sesion_cronometro.py
# Pruebas de la mini-tarea previa a C6: DELETE /sesiones-cronometro/{id_sesion}/descartar
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1.endpoints import sesiones_cronometro as endpoints
from app.models.sesion_cronometro import SesionCronometro
from app.services import sesion_cronometro_service


def _sesion(id_sesion=5, id_usuario=12, fecha_fin=None):
    return SimpleNamespace(
        id_sesion=id_sesion,
        id_usuario=id_usuario,
        fecha_inicio=datetime(2026, 11, 2, 10, 0, 0),
        fecha_fin=fecha_fin,
        duracion=None,
    )


class DescartarSesionValidacionesTests(unittest.TestCase):
    """Errores del service: sesión inexistente, ajena o ya finalizada."""

    def test_sesion_inexistente_devuelve_404(self):
        with patch.object(
            sesion_cronometro_service.repo, "get_sesion_by_id", return_value=None
        ):
            with self.assertRaises(HTTPException) as error:
                sesion_cronometro_service.descartar_sesion(None, 5, 12)

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, "Sesión no encontrada")

    def test_sesion_de_otro_usuario_devuelve_404(self):
        ajeno = _sesion(id_usuario=99)
        with patch.object(
            sesion_cronometro_service.repo, "get_sesion_by_id", return_value=ajeno
        ):
            with self.assertRaises(HTTPException) as error:
                sesion_cronometro_service.descartar_sesion(None, 5, 12)

        self.assertEqual(error.exception.status_code, 404)

    def test_sesion_ya_finalizada_devuelve_400(self):
        cerrada = _sesion(fecha_fin=datetime(2026, 11, 2, 11, 0, 0))
        with patch.object(
            sesion_cronometro_service.repo, "get_sesion_by_id", return_value=cerrada
        ):
            with self.assertRaises(HTTPException) as error:
                sesion_cronometro_service.descartar_sesion(None, 5, 12)

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "La sesión ya fue finalizada")


class DescartarSesionExitosoTests(unittest.TestCase):
    """Caso feliz con mocks: borra la sesión abierta del dueño."""

    def test_sesion_abierta_se_borra(self):
        abierta = _sesion()
        with patch.object(
            sesion_cronometro_service.repo, "get_sesion_by_id", return_value=abierta
        ), patch.object(
            sesion_cronometro_service.repo, "delete_sesion"
        ) as borrar:
            sesion_cronometro_service.descartar_sesion(None, 5, 12)

        borrar.assert_called_once_with(None, abierta)


class DescartarSesionIntegracionTests(unittest.TestCase):
    """Caso feliz contra SQLite: la fila desaparece de la tabla."""

    def test_la_fila_se_elimina_de_la_base(self):
        engine = create_engine("sqlite+pysqlite:///:memory:")
        SesionCronometro.__table__.create(engine)
        try:
            with Session(engine) as db:
                sesion = SesionCronometro(
                    fecha_inicio=datetime(2026, 11, 2, 10, 0, 0),
                    id_tarea=4,
                    id_usuario=8,
                )
                db.add(sesion)
                db.commit()
                db.refresh(sesion)
                id_sesion = sesion.id_sesion

                sesion_cronometro_service.descartar_sesion(db, id_sesion, 8)

                borrada = (
                    db.query(SesionCronometro)
                    .filter(SesionCronometro.id_sesion == id_sesion)
                    .first()
                )
                self.assertIsNone(borrada)
        finally:
            engine.dispose()


class DescartarSesionEndpointTests(unittest.TestCase):
    """El endpoint delega en el service con el usuario del JWT."""

    def test_endpoint_llama_al_service_con_el_usuario_actual(self):
        usuario_actual = SimpleNamespace(id_usuario=12)
        with patch.object(endpoints.service, "descartar_sesion") as descartar:
            resultado = endpoints.descartar_sesion(5, None, usuario_actual)

        descartar.assert_called_once_with(None, 5, 12)
        self.assertIsNone(resultado)
