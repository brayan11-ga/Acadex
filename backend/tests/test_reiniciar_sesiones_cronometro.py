# Ruta: backend/tests/test_reiniciar_sesiones_cronometro.py
# Pruebas de C6b Parte 2: DELETE /sesiones-cronometro/tarea/{id_tarea}/reiniciar
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1.endpoints import sesiones_cronometro as endpoints
from app.models.historial_tarea import HistorialTarea
from app.models.sesion_cronometro import SesionCronometro
from app.repositories import historial_tarea_repository
from app.services import sesion_cronometro_service, tarea_service


def _tarea_grupal(id_tarea=4, id_grupo=3):
    return SimpleNamespace(id_tarea=id_tarea, id_usuario=None, id_grupo=id_grupo)


class ReiniciarSesionesServiceTests(unittest.TestCase):
    """Validaciones del service: 404, 403, 409 y caso feliz."""

    def test_tarea_inexistente_devuelve_404(self):
        with patch.object(
            tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=None
        ):
            with self.assertRaises(HTTPException) as error:
                sesion_cronometro_service.reiniciar_sesiones_tarea(None, 12, 4)
        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, "Tarea no encontrada")

    def test_usuario_no_asignado_devuelve_403(self):
        with (
            patch.object(
                tarea_service.tarea_repository,
                "obtener_tarea_por_id",
                return_value=_tarea_grupal(),
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "usuario_tiene_asignacion",
                return_value=False,
            ),
        ):
            with self.assertRaises(HTTPException) as error:
                sesion_cronometro_service.reiniciar_sesiones_tarea(None, 12, 4)
        self.assertEqual(error.exception.status_code, 403)

    def test_ya_completado_devuelve_409(self):
        with (
            patch.object(
                tarea_service.tarea_repository,
                "obtener_tarea_por_id",
                return_value=_tarea_grupal(),
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "usuario_tiene_asignacion",
                return_value=True,
            ),
            patch.object(
                historial_tarea_repository,
                "usuario_ya_completo",
                return_value=True,
            ),
        ):
            with self.assertRaises(HTTPException) as error:
                sesion_cronometro_service.reiniciar_sesiones_tarea(None, 12, 4)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(
            error.exception.detail,
            "Ya completaste tu parte. Para reiniciar el cronómetro, "
            "el líder debe reabrir la tarea.",
        )

    def test_caso_feliz_delega_en_el_repositorio(self):
        with (
            patch.object(
                tarea_service.tarea_repository,
                "obtener_tarea_por_id",
                return_value=_tarea_grupal(),
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "usuario_tiene_asignacion",
                return_value=True,
            ),
            patch.object(
                historial_tarea_repository, "usuario_ya_completo", return_value=False
            ),
            patch.object(
                sesion_cronometro_service.repo,
                "reiniciar_sesiones_usuario_tarea",
            ) as borrar,
        ):
            resultado = sesion_cronometro_service.reiniciar_sesiones_tarea(None, 12, 4)
        borrar.assert_called_once_with(None, 4, 12)
        self.assertIsNone(resultado)


class ReiniciarSesionesIntegracionTests(unittest.TestCase):
    """Caso real contra SQLite: borra solo lo del usuario en esa tarea."""

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        SesionCronometro.__table__.create(self.engine)
        HistorialTarea.__table__.create(self.engine)
        self.db = Session(self.engine)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _sesion(self, id_tarea, id_usuario, fecha_fin=None, duracion=None):
        return SesionCronometro(
            fecha_inicio=datetime(2026, 11, 11, 10, 0, 0),
            fecha_fin=fecha_fin,
            duracion=duracion,
            id_tarea=id_tarea,
            id_usuario=id_usuario,
        )

    def test_borra_abiertas_y_cerradas_del_usuario_y_respeta_a_los_demas(self):
        self.db.add_all(
            [
                self._sesion(4, 8),
                self._sesion(
                    4, 8, fecha_fin=datetime(2026, 11, 11, 11), duracion=60.0
                ),
                self._sesion(4, 9),
                self._sesion(5, 8),
            ]
        )
        self.db.commit()

        with patch.object(tarea_service, "verificar_permiso_tarea"):
            sesion_cronometro_service.reiniciar_sesiones_tarea(self.db, 8, 4)

        restantes = self.db.query(SesionCronometro).all()
        self.assertEqual(len(restantes), 2)
        self.assertEqual(
            {(sesion.id_tarea, sesion.id_usuario) for sesion in restantes},
            {(4, 9), (5, 8)},
        )

    def test_409_si_ya_completo_y_feliz_tras_borrar_el_historial(self):
        self.db.add(self._sesion(4, 8))
        self.db.add(
            HistorialTarea(
                id_tarea=4,
                id_usuario=8,
                id_grupo=3,
                fechahora_fin=datetime(2026, 11, 11, 12, 0, 0),
                tiempo_real=60.0,
                dificultad_real=3,
            )
        )
        self.db.commit()

        with patch.object(tarea_service, "verificar_permiso_tarea"):
            with self.assertRaises(HTTPException) as error:
                sesion_cronometro_service.reiniciar_sesiones_tarea(self.db, 8, 4)
            self.assertEqual(error.exception.status_code, 409)
            self.assertEqual(self.db.query(SesionCronometro).count(), 1)

            # Como tras `reabrir`: se borra el historial y se conservan las sesiones.
            self.db.query(HistorialTarea).delete()
            self.db.commit()

            sesion_cronometro_service.reiniciar_sesiones_tarea(self.db, 8, 4)

        self.assertEqual(self.db.query(SesionCronometro).count(), 0)


class ReiniciarSesionesEndpointTests(unittest.TestCase):
    """El endpoint delega en el service con el usuario del JWT."""

    def test_endpoint_llama_al_service_con_el_usuario_actual(self):
        usuario_actual = SimpleNamespace(id_usuario=12)
        with patch.object(endpoints.service, "reiniciar_sesiones_tarea") as reiniciar:
            resultado = endpoints.reiniciar_sesiones_tarea(4, None, usuario_actual)
        reiniciar.assert_called_once_with(None, 12, 4)
        self.assertIsNone(resultado)


if __name__ == "__main__":
    unittest.main()
