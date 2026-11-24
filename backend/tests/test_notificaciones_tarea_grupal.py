# Ruta: backend/tests/test_notificaciones_tarea_grupal.py
# Pruebas de C9 Parte 3: notificaciones al eliminar una tarea grupal y al
# cambiar su fecha de entrega. Las tareas individuales no deben generar avisos.
import unittest
from contextlib import contextmanager
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.schemas.tarea import TareaUpdate
from app.services import tarea_service


def _tarea(
    estado="en progreso",
    nombre="Tarea de prueba",
    grupal=True,
):
    return SimpleNamespace(
        id_tarea=4,
        id_usuario=None if grupal else 12,
        id_grupo=7 if grupal else None,
        id_categoria=1,
        estado=estado,
        nombre=nombre,
        fecha_entrega=datetime(2026, 10, 30, 23, 59),
        dificultad_estimada=3,
        tiempo_acumulado=0.0,
        total_archivos=0,
    )


@contextmanager
def _cuarentena_vacia(_db, _id_tarea):
    yield


class EliminarTareaNotificacionesTests(unittest.TestCase):
    """DELETE /tareas/{id}: avisa a asignados (menos al líder), siempre grupal."""

    def _ejecutar(self, tarea, asignados=None, fallar=False):
        db = Mock()
        usuarios = [SimpleNamespace(id_usuario=i) for i in (asignados or [])]
        with (
            patch.object(
                tarea_service.tarea_repository,
                "obtener_tarea_por_id",
                return_value=tarea,
            ),
            patch.object(
                tarea_service.grupo_repository,
                "obtener_integrante",
                return_value=SimpleNamespace(rol="lider"),
            ),
            patch.object(
                tarea_service.archivo_repository,
                "contar_archivos_de_tarea",
                return_value=0,
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "obtener_usuarios_asignados",
                return_value=usuarios,
            ),
            patch.object(
                tarea_service.archivo_service,
                "preparar_eliminacion_archivos_tarea",
                _cuarentena_vacia,
            ),
            patch.object(
                tarea_service.tarea_repository,
                "eliminar_tarea",
                side_effect=RuntimeError("fallo de borrado") if fallar else None,
            ) as eliminar,
            patch.object(
                tarea_service.notificacion_repository, "crear_notificacion"
            ) as notificar,
        ):
            if fallar:
                with self.assertRaises(RuntimeError):
                    tarea_service.eliminar_tarea(db, 4, 12)
            else:
                tarea_service.eliminar_tarea(db, 4, 12)
        return db, eliminar, notificar

    def test_avisa_a_asignados_menos_al_lider(self):
        _, eliminar, notificar = self._ejecutar(
            _tarea(), asignados=[12, 13, 14]
        )
        eliminar.assert_called_once()
        self.assertEqual(notificar.call_count, 2)
        destinatarios = {
            llamada.kwargs["id_usuario"] for llamada in notificar.call_args_list
        }
        self.assertEqual(destinatarios, {13, 14})
        for llamada in notificar.call_args_list:
            kwargs = llamada.kwargs
            self.assertEqual(kwargs["titulo"], "Tarea eliminada")
            self.assertEqual(kwargs["tipo"], "tarea_eliminada")
            # Sin id_tarea: la tarea se borra y la FK está en cascada.
            self.assertIsNone(kwargs["id_tarea"])
            self.assertFalse(kwargs["commit"])
            self.assertIn("Tarea de prueba", kwargs["detalles"])

    def test_sin_asignados_no_avisa(self):
        _, _, notificar = self._ejecutar(_tarea(), asignados=[])
        notificar.assert_not_called()

    def test_si_el_borrado_falla_no_se_commitea_nada(self):
        db, eliminar, notificar = self._ejecutar(
            _tarea(), asignados=[12, 13, 14], fallar=True
        )
        eliminar.assert_called_once()
        # Las notificaciones se crean con commit=False: si el borrado falla,
        # se descartan con el rollback de la transacción.
        self.assertEqual(notificar.call_count, 2)
        for llamada in notificar.call_args_list:
            self.assertFalse(llamada.kwargs["commit"])
        db.commit.assert_not_called()

    def test_tarea_individual_no_avisa(self):
        _, eliminar, notificar = self._ejecutar(
            _tarea(grupal=False), asignados=[12]
        )
        eliminar.assert_called_once()
        notificar.assert_not_called()

    def test_nombre_de_50_caracteres_se_recorta_y_cabe_en_100(self):
        nombre = "Tarea " + "x" * 44
        self.assertEqual(len(nombre), 50)
        _, _, notificar = self._ejecutar(_tarea(nombre=nombre), asignados=[13])
        detalle = notificar.call_args_list[0].kwargs["detalles"]
        self.assertIn("…", detalle)
        self.assertNotIn(nombre, detalle)
        self.assertLessEqual(len(detalle), 100)


class CambiarFechaNotificacionesTests(unittest.TestCase):
    """PUT /tareas/{id}: avisa solo si la fecha cambió de verdad y es grupal."""

    def _ejecutar(self, tarea, fecha_iso, asignados=(13, 14)):
        db = Mock()
        # El schema Pydantic parsea el ISO a datetime: misma prueba que el endpoint.
        datos = TareaUpdate(fecha_entrega=fecha_iso)
        usuarios = [SimpleNamespace(id_usuario=i) for i in asignados]
        with (
            patch.object(
                tarea_service.tarea_repository,
                "obtener_tarea_por_id",
                return_value=tarea,
            ),
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(
                tarea_service.archivo_repository,
                "contar_archivos_de_tarea",
                return_value=0,
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "obtener_usuarios_asignados",
                return_value=usuarios,
            ) as obtener_asignados,
            patch.object(
                tarea_service.notificacion_repository, "crear_notificacion"
            ) as notificar,
        ):
            tarea_service.actualizar_tarea(db, 4, datos, 12)
        return notificar, obtener_asignados

    def test_misma_fecha_no_avisa(self):
        # 2026-10-30T23:59 se parsea igual que la fecha guardada.
        notificar, obtener_asignados = self._ejecutar(
            _tarea(), "2026-10-30T23:59"
        )
        notificar.assert_not_called()
        obtener_asignados.assert_not_called()

    def test_fecha_nueva_avisa_a_asignados_menos_al_lider(self):
        notificar, _ = self._ejecutar(_tarea(), "2026-11-15T10:30")
        self.assertEqual(notificar.call_count, 2)
        destinatarios = {
            llamada.kwargs["id_usuario"] for llamada in notificar.call_args_list
        }
        self.assertEqual(destinatarios, {13, 14})
        for llamada in notificar.call_args_list:
            kwargs = llamada.kwargs
            self.assertEqual(kwargs["titulo"], "Cambió la fecha de entrega")
            self.assertEqual(kwargs["tipo"], "tarea_fecha_cambiada")
            self.assertEqual(kwargs["id_tarea"], 4)
            self.assertFalse(kwargs["commit"])
            self.assertIn("de 30 oct. a 15 nov.", kwargs["detalles"])

    def test_sin_asignados_no_avisa(self):
        notificar, _ = self._ejecutar(
            _tarea(), "2026-11-15T10:30", asignados=()
        )
        notificar.assert_not_called()

    def test_tarea_individual_no_avisa(self):
        tarea = _tarea(grupal=False)
        db = Mock()
        datos = TareaUpdate(fecha_entrega="2026-11-15T10:30")
        with (
            patch.object(
                tarea_service.tarea_repository,
                "obtener_tarea_por_id",
                return_value=tarea,
            ),
            patch.object(
                tarea_service.archivo_repository,
                "contar_archivos_de_tarea",
                return_value=0,
            ),
            patch.object(
                tarea_service.notificacion_repository, "crear_notificacion"
            ) as notificar,
        ):
            resultado = tarea_service.actualizar_tarea(db, 4, datos, 12)
        notificar.assert_not_called()
        # La tarea individual sigue actualizándose con normalidad.
        self.assertEqual(resultado.fecha_entrega, datetime(2026, 11, 15, 10, 30))

    def test_nombre_de_50_caracteres_se_recorta_y_cabe_en_100(self):
        nombre = "Tarea " + "x" * 44
        self.assertEqual(len(nombre), 50)
        notificar, _ = self._ejecutar(
            _tarea(nombre=nombre), "2026-11-15T10:30", asignados=(13,)
        )
        detalle = notificar.call_args_list[0].kwargs["detalles"]
        self.assertIn("…", detalle)
        self.assertNotIn(nombre, detalle)
        self.assertLessEqual(len(detalle), 100)


class ComparacionFechaTests(unittest.TestCase):
    """La comparación es datetime contra datetime, nunca fecha contra texto."""

    def test_misma_fecha_en_minutos_no_cuenta_como_cambio(self):
        tarea = _tarea()
        cambios = {"fecha_entrega": datetime(2026, 10, 30, 23, 59, 30)}
        self.assertFalse(
            tarea_service._cambio_fecha_entrega(
                tarea, cambios, datetime(2026, 10, 30, 23, 59)
            )
        )

    def test_fecha_distinta_cuenta_como_cambio(self):
        tarea = _tarea()
        cambios = {"fecha_entrega": datetime(2026, 11, 15, 10, 30)}
        self.assertTrue(
            tarea_service._cambio_fecha_entrega(
                tarea, cambios, datetime(2026, 10, 30, 23, 59)
            )
        )

    def test_individual_nunca_cuenta_como_cambio(self):
        tarea = _tarea(grupal=False)
        cambios = {"fecha_entrega": datetime(2026, 11, 15, 10, 30)}
        self.assertFalse(
            tarea_service._cambio_fecha_entrega(
                tarea, cambios, datetime(2026, 10, 30, 23, 59)
            )
        )


if __name__ == "__main__":
    unittest.main()
