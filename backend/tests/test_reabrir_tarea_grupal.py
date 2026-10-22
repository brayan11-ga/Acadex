# Ruta: backend/tests/test_reabrir_tarea_grupal.py
# Pruebas de la Fase C4b. SIN VERIFICAR: no se ejecutaron en esta sesión.
# Sam debe correrlas con `python -m unittest tests.test_reabrir_tarea_grupal`.
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.services import tarea_service


def _tarea_grupal(estado="Completada", nombre="Tarea de prueba"):
    return SimpleNamespace(
        id_tarea=4,
        id_usuario=None,
        id_grupo=7,
        id_categoria=1,
        estado=estado,
        nombre=nombre,
        dificultad_estimada=3,
        tiempo_acumulado=0.0,
    )


class ReabrirValidacionesTests(unittest.TestCase):
    """Escenarios de error del POST /tareas/{id}/reabrir."""

    def test_tarea_inexistente_devuelve_404(self):
        with patch.object(
            tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=None
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reabrir_tarea_grupal(Mock(), 4, 12)
        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, "Tarea no encontrada")

    def test_tarea_individual_devuelve_400(self):
        tarea = SimpleNamespace(
            id_tarea=4, id_usuario=12, id_grupo=None, estado="Completada"
        )
        with patch.object(
            tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reabrir_tarea_grupal(Mock(), 4, 12)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(
            error.exception.detail,
            "Esta tarea no es grupal; usa el flujo actual (PUT).",
        )

    def test_no_lider_devuelve_403(self):
        tarea = _tarea_grupal()
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(tarea_service, "_es_lider", return_value=False),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reabrir_tarea_grupal(Mock(), 4, 13)
        self.assertEqual(error.exception.status_code, 403)
        self.assertEqual(
            error.exception.detail, "Solo el líder del grupo puede reabrir esta tarea."
        )

    def test_tarea_no_completada_devuelve_409(self):
        tarea = _tarea_grupal(estado="en progreso")
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(tarea_service, "_es_lider", return_value=True),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reabrir_tarea_grupal(Mock(), 4, 12)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(error.exception.detail, "La tarea no está completada.")


class ReabrirExitosoTests(unittest.TestCase):
    """Camino feliz: estado, borrado de historial y notificaciones."""

    def _ejecutar(self, nombre="Tarea de prueba", asignados=None):
        tarea = _tarea_grupal(nombre=nombre)
        db = Mock()
        asignados = asignados or [
            SimpleNamespace(id_usuario=12),
            SimpleNamespace(id_usuario=13),
            SimpleNamespace(id_usuario=14),
        ]
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(
                tarea_service.historial_tarea_repository, "eliminar_por_tarea"
            ) as eliminar,
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "obtener_usuarios_asignados",
                return_value=asignados,
            ),
            patch.object(
                tarea_service.archivo_repository, "contar_archivos_de_tarea", return_value=2
            ),
            patch.object(
                tarea_service.notificacion_repository, "crear_notificacion"
            ) as notificar,
        ):
            resultado = tarea_service.reabrir_tarea_grupal(db, 4, 12)
        return resultado, eliminar, notificar, db

    def test_lider_reabre_y_estado_queda_en_progreso(self):
        resultado, eliminar, _, db = self._ejecutar()
        self.assertEqual(resultado.estado, "en progreso")
        eliminar.assert_called_once_with(db, 4)
        db.commit.assert_called_once()
        self.assertEqual(resultado.total_archivos, 2)

    def test_notifica_a_asignados_excepto_al_lider(self):
        _, _, notificar, _ = self._ejecutar()
        self.assertEqual(notificar.call_count, 2)
        usuarios_notificados = {
            llamada.kwargs["id_usuario"] for llamada in notificar.call_args_list
        }
        self.assertEqual(usuarios_notificados, {13, 14})
        for llamada in notificar.call_args_list:
            kwargs = llamada.kwargs
            self.assertEqual(
                kwargs["titulo"], "Una tarea volvió a estar en progreso"
            )
            self.assertEqual(
                kwargs["detalles"],
                "El líder reabrió «Tarea de prueba». Debes completar tu parte otra vez.",
            )
            self.assertEqual(kwargs["tipo"], "tarea_reabierta")
            self.assertEqual(kwargs["id_tarea"], 4)

    def test_titulo_y_detalle_respetan_los_limites(self):
        _, _, notificar, _ = self._ejecutar()
        for llamada in notificar.call_args_list:
            self.assertLessEqual(len(llamada.kwargs["titulo"]), 50)
            self.assertLessEqual(len(llamada.kwargs["detalles"]), 100)

    def test_no_recalcula_estadistica(self):
        with patch(
            "app.services.estadistica_service.recalcular_estadistica_categoria"
        ) as recalcular:
            self._ejecutar()
        recalcular.assert_not_called()

    def test_nombre_largo_se_recorta_a_35_con_punto_suspensivo(self):
        nombre = "Tarea con un nombre realmente largo para notificar"
        _, _, notificar, _ = self._ejecutar(nombre=nombre)
        detalle = notificar.call_args_list[0].kwargs["detalles"]
        self.assertIn("…", detalle)
        self.assertLessEqual(len(detalle), 100)
        self.assertNotIn(nombre, detalle)

    def test_si_el_lider_no_esta_asignado_se_notifica_a_todos(self):
        _, _, notificar, _ = self._ejecutar(
            asignados=[
                SimpleNamespace(id_usuario=13),
                SimpleNamespace(id_usuario=14),
            ]
        )
        self.assertEqual(notificar.call_count, 2)

    def test_si_falla_una_notificacion_no_se_deshace_la_reapertura(self):
        tarea = _tarea_grupal()
        db = Mock()
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(
                tarea_service.historial_tarea_repository, "eliminar_por_tarea"
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "obtener_usuarios_asignados",
                return_value=[SimpleNamespace(id_usuario=13)],
            ),
            patch.object(
                tarea_service.archivo_repository,
                "contar_archivos_de_tarea",
                return_value=0,
            ),
            patch.object(
                tarea_service.notificacion_repository,
                "crear_notificacion",
                side_effect=RuntimeError("fallo sintético"),
            ),
        ):
            resultado = tarea_service.reabrir_tarea_grupal(db, 4, 12)
        self.assertEqual(resultado.estado, "en progreso")
        db.commit.assert_called_once()


class RecorteNombreTests(unittest.TestCase):
    def test_nombre_corto_no_cambia(self):
        self.assertEqual(
            tarea_service._recortar_nombre_tarea("Tarea corta"), "Tarea corta"
        )

    def test_nombre_largo_termina_en_punto_suspensivo_y_mide_35(self):
        recortado = tarea_service._recortar_nombre_tarea("x" * 80)
        self.assertEqual(len(recortado), 35)
        self.assertTrue(recortado.endswith("…"))


if __name__ == "__main__":
    unittest.main()
