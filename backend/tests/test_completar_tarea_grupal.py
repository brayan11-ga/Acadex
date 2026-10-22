# Ruta: backend/tests/test_completar_tarea_grupal.py
# Pruebas de la Tarea C3. SIN VERIFICAR: no se ejecutaron en esta sesión;
# Sam debe correrlas con `python -m unittest tests.test_completar_tarea_grupal`.
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.schemas.tarea import CompletarTareaRequest
from app.services import tarea_service


def _tarea_grupal(estado="pendiente"):
    return SimpleNamespace(
        id_tarea=4,
        id_usuario=None,
        id_grupo=7,
        id_categoria=1,
        estado=estado,
        dificultad_estimada=3,
        tiempo_acumulado=0.0,
    )


class CompletarParteValidacionesTests(unittest.TestCase):
    """Escenarios de error del POST /tareas/{id}/completar."""

    def test_tarea_individual_devuelve_400(self):
        tarea = SimpleNamespace(id_tarea=4, id_usuario=12, id_grupo=None, estado="pendiente")
        with patch.object(
            tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.completar_parte_tarea(Mock(), 4, 3, 12)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(
            error.exception.detail,
            "Esta tarea no es grupal; usa el flujo actual (PUT).",
        )

    def test_usuario_no_asignado_devuelve_403(self):
        tarea = _tarea_grupal()
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "usuario_tiene_asignacion",
                return_value=False,
            ),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.completar_parte_tarea(Mock(), 4, 3, 99)
        self.assertEqual(error.exception.status_code, 403)

    def test_tarea_ya_completada_devuelve_409(self):
        tarea = _tarea_grupal(estado="Completada")
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "usuario_tiene_asignacion",
                return_value=True,
            ),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.completar_parte_tarea(Mock(), 4, 3, 12)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(error.exception.detail, "La tarea ya está completada.")

    def test_usuario_que_ya_completo_su_parte_devuelve_409(self):
        tarea = _tarea_grupal()
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "usuario_tiene_asignacion",
                return_value=True,
            ),
            patch.object(
                tarea_service.historial_tarea_repository,
                "usuario_ya_completo",
                return_value=True,
            ),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.completar_parte_tarea(Mock(), 4, 3, 12)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(
            error.exception.detail, "Ya completaste tu parte de esta tarea."
        )

    def test_cronometro_abierto_del_mismo_usuario_devuelve_409(self):
        tarea = _tarea_grupal()
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "usuario_tiene_asignacion",
                return_value=True,
            ),
            patch.object(
                tarea_service.historial_tarea_repository,
                "usuario_ya_completo",
                return_value=False,
            ),
            patch.object(
                tarea_service.sesion_cronometro_repository,
                "get_sesion_activa_de_usuario",
                return_value=SimpleNamespace(id_sesion=1),
            ),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.completar_parte_tarea(Mock(), 4, 3, 12)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(
            error.exception.detail,
            "Pausa tu cronómetro antes de completar tu parte.",
        )


class CompletarParteExitosoTests(unittest.TestCase):
    """Camino feliz: tiempo real, id_grupo y cambio de estado."""

    def _ejecutar(self, completados, usuarios_asignados, tiempo=125.0):
        tarea = _tarea_grupal()
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "usuario_tiene_asignacion",
                return_value=True,
            ),
            patch.object(
                tarea_service.historial_tarea_repository,
                "usuario_ya_completo",
                return_value=False,
            ),
            patch.object(
                tarea_service.sesion_cronometro_repository,
                "get_sesion_activa_de_usuario",
                return_value=None,
            ),
            patch.object(
                tarea_service.sesion_cronometro_repository,
                "sumar_duracion_cerrada",
                return_value=tiempo,
            ),
            patch.object(
                tarea_service.historial_tarea_repository, "upsert"
            ) as upsert,
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "obtener_usuarios_asignados",
                return_value=usuarios_asignados,
            ),
            patch.object(
                tarea_service.historial_tarea_repository,
                "obtener_usuarios_completados",
                return_value=completados,
            ),
            patch.object(
                tarea_service.archivo_repository,
                "contar_archivos_de_tarea",
                return_value=0,
            ),
        ):
            resultado = tarea_service.completar_parte_tarea(Mock(), 4, 4, 12)
        return resultado, upsert

    def test_guarda_tiempo_real_de_sesiones_cerradas_y_marca_en_progreso(self):
        resultado, upsert = self._ejecutar(
            completados={12},
            usuarios_asignados=[
                SimpleNamespace(id_usuario=12),
                SimpleNamespace(id_usuario=13),
            ],
        )
        upsert.assert_called_once()
        _, kwargs = upsert.call_args
        self.assertEqual(kwargs["dificultad_real"], 4)
        self.assertEqual(kwargs["tiempo_real"], 125.0)
        self.assertEqual(kwargs["id_grupo"], 7)
        self.assertEqual(resultado.estado, "en progreso")

    def test_marca_completada_cuando_todos_los_asignados_completaron(self):
        resultado, _ = self._ejecutar(
            completados={12, 13},
            usuarios_asignados=[
                SimpleNamespace(id_usuario=12),
                SimpleNamespace(id_usuario=13),
            ],
        )
        self.assertEqual(resultado.estado, "Completada")

    def test_no_llama_recalcular_estadistica(self):
        with patch(
            "app.services.estadistica_service.recalcular_estadistica_categoria"
        ) as recalcular:
            self._ejecutar(
                completados={12},
                usuarios_asignados=[SimpleNamespace(id_usuario=12)],
            )
        recalcular.assert_not_called()


class DificultadRealSchemaTests(unittest.TestCase):
    def test_rechaza_dificultad_menor_a_1(self):
        with self.assertRaises(Exception):
            CompletarTareaRequest(dificultad_real=0)

    def test_rechaza_dificultad_mayor_a_5(self):
        with self.assertRaises(Exception):
            CompletarTareaRequest(dificultad_real=6)

    def test_acepta_dificultad_valida(self):
        self.assertEqual(CompletarTareaRequest(dificultad_real=3).dificultad_real, 3)


class RestriccionesPutGrupalTests(unittest.TestCase):
    """El PUT ya no permite moverse libremente en las tareas grupales."""

    def _ejecutar(self, tarea, datos, es_lider):
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service, "_es_lider", return_value=es_lider),
            patch.object(
                tarea_service.tarea_repository, "actualizar_tarea"
            ) as actualizar,
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.actualizar_tarea(Mock(), 4, datos, 12)
        return error.exception, actualizar

    def test_no_lider_no_puede_modificar_nada(self):
        error, actualizar = self._ejecutar(
            _tarea_grupal(), tarea_service.TareaUpdate(nombre="Nuevo"), False
        )
        self.assertEqual(error.status_code, 403)
        actualizar.assert_not_called()

    def test_nadie_edita_una_tarea_completada_ni_el_lider(self):
        error, actualizar = self._ejecutar(
            _tarea_grupal(estado="Completada"),
            tarea_service.TareaUpdate(nombre="Nuevo"),
            True,
        )
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.detail, "Reábrila primero.")
        actualizar.assert_not_called()

    def test_put_no_puede_marcar_completada(self):
        error, actualizar = self._ejecutar(
            _tarea_grupal(),
            tarea_service.TareaUpdate(estado="Completada"),
            True,
        )
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.detail, "Usa Completar mi parte.")
        actualizar.assert_not_called()

    def test_put_no_puede_cambiar_el_estado(self):
        error, actualizar = self._ejecutar(
            _tarea_grupal(),
            tarea_service.TareaUpdate(estado="en progreso"),
            True,
        )
        self.assertEqual(error.status_code, 400)
        self.assertIn("No puedes cambiar el estado", error.detail)
        actualizar.assert_not_called()

    def test_lider_si_puede_editar_otros_campos(self):
        tarea = _tarea_grupal()
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(
                tarea_service.tarea_repository,
                "actualizar_tarea",
                return_value=tarea,
            ) as actualizar,
        ):
            tarea_service.actualizar_tarea(
                Mock(), 4, tarea_service.TareaUpdate(nombre="Nuevo"), 12
            )
        actualizar.assert_called_once()


class AsignadosConCompletadoTests(unittest.TestCase):
    def test_lista_incluye_campo_completado(self):
        tarea = _tarea_grupal()
        usuarios = [
            SimpleNamespace(id_usuario=12, correo_electronico="a@a.com"),
            SimpleNamespace(id_usuario=13, correo_electronico="b@b.com"),
        ]
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "obtener_usuarios_asignados",
                return_value=usuarios,
            ),
            patch.object(
                tarea_service.historial_tarea_repository,
                "obtener_usuarios_completados",
                return_value={12},
            ),
        ):
            resultado = tarea_service.listar_asignados_de_tarea(Mock(), 4, 12)
        self.assertTrue(resultado[0]["completado"])
        self.assertFalse(resultado[1]["completado"])


if __name__ == "__main__":
    unittest.main()
