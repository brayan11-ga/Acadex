# Ruta: backend/tests/test_reasignar_tarea_grupal.py
# Pruebas de la Fase C4c. SIN VERIFICAR: no se ejecutaron en esta sesión.
# Sam debe correrlas con `python -m unittest tests.test_reasignar_tarea_grupal`.
import tempfile
import unittest
from contextlib import ExitStack, contextmanager
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.services import archivo_service, tarea_service


def _tarea_grupal(estado="pendiente", nombre="Tarea de prueba"):
    return SimpleNamespace(
        id_tarea=4,
        id_usuario=None,
        id_grupo=7,
        id_categoria=1,
        estado=estado,
        nombre=nombre,
        fecha_entrega=datetime(2026, 10, 30, 23, 59),
        dificultad_estimada=3,
        tiempo_acumulado=0.0,
    )


class ReasignarValidacionesTests(unittest.TestCase):
    """Escenarios de error del PUT /tareas/{id}/asignados."""

    def test_tarea_inexistente_devuelve_404(self):
        with patch.object(
            tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=None
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reasignar_asignados_tarea(Mock(), 4, [12], 12)
        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, "Tarea no encontrada")

    def test_tarea_individual_devuelve_400(self):
        tarea = SimpleNamespace(
            id_tarea=4, id_usuario=12, id_grupo=None, estado="pendiente"
        )
        with patch.object(
            tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reasignar_asignados_tarea(Mock(), 4, [12], 12)
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
                tarea_service.reasignar_asignados_tarea(Mock(), 4, [12], 13)
        self.assertEqual(error.exception.status_code, 403)
        self.assertEqual(
            error.exception.detail,
            "Solo el líder del grupo puede reasignar esta tarea.",
        )

    def test_tarea_completada_devuelve_409(self):
        tarea = _tarea_grupal(estado="Completada")
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(tarea_service, "_es_lider", return_value=True),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reasignar_asignados_tarea(Mock(), 4, [12], 12)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(error.exception.detail, "Reábrela primero.")

    def test_lista_vacia_devuelve_400(self):
        tarea = _tarea_grupal()
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(tarea_service, "_es_lider", return_value=True),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reasignar_asignados_tarea(Mock(), 4, [], 12)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(
            error.exception.detail, "La tarea debe tener al menos un asignado."
        )

    def test_ids_repetidos_devuelven_400(self):
        tarea = _tarea_grupal()
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(tarea_service, "_es_lider", return_value=True),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reasignar_asignados_tarea(Mock(), 4, [12, 12], 12)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(
            error.exception.detail, "No se permiten asignados repetidos."
        )

    def test_usuario_fuera_del_grupo_devuelve_400(self):
        tarea = _tarea_grupal()
        with (
            patch.object(
                tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea
            ),
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(
                tarea_service.grupo_repository, "obtener_integrante", return_value=None
            ),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.reasignar_asignados_tarea(Mock(), 4, [99], 12)
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(
            error.exception.detail,
            "Todos los asignados deben pertenecer a este grupo.",
        )


class ReasignarExitosoTests(unittest.TestCase):
    """Camino feliz: borrado del avance, altas nuevas y notificaciones."""

    def _ejecutar(
        self,
        ids_nuevos,
        asignados_actuales,
        asignados_finales,
        completados=None,
        archivos_por_usuario=None,
        sesiones_por_usuario=None,
        historial_por_usuario=None,
        estado="pendiente",
        nombre="Tarea de prueba",
        cuarentena=None,
    ):
        tarea = _tarea_grupal(estado=estado, nombre=nombre)
        db = Mock()
        completados = completados or set()
        archivos_por_usuario = archivos_por_usuario or {}
        sesiones_por_usuario = sesiones_por_usuario or {}
        historial_por_usuario = historial_por_usuario or set()
        usuarios_actuales = [SimpleNamespace(id_usuario=i) for i in asignados_actuales]
        usuarios_finales = [SimpleNamespace(id_usuario=i) for i in asignados_finales]
        llamadas = {"asignados": 0}

        def _obtener_asignados(_db, _id_tarea):
            llamadas["asignados"] += 1
            if llamadas["asignados"] == 1:
                return usuarios_actuales
            return usuarios_finales

        def _obtener_integrante(_db, id_usuario, _id_grupo):
            return SimpleNamespace(
                id_integrante=100 + id_usuario,
                id_usuario=id_usuario,
                rol="miembro",
            )

        def _obtener_archivos(_db, _id_tarea, ids_usuarios):
            return archivos_por_usuario.get(ids_usuarios[0], [])

        def _obtener_sesiones(_db, _id_tarea, id_usuario):
            return sesiones_por_usuario.get(id_usuario, [])

        def _obtener_fila(_db, id_usuario, _id_tarea):
            if id_usuario in historial_por_usuario:
                return SimpleNamespace(id_historial=1)
            return None

        @contextmanager
        def _cuarentena(_db, _id_tarea, _ids_usuarios):
            yield

        with ExitStack() as stack:
            mocks = {}
            mocks["obtener_tarea"] = stack.enter_context(
                patch.object(
                    tarea_service.tarea_repository,
                    "obtener_tarea_por_id",
                    return_value=tarea,
                )
            )
            mocks["es_lider"] = stack.enter_context(
                patch.object(tarea_service, "_es_lider", return_value=True)
            )
            mocks["obtener_integrante"] = stack.enter_context(
                patch.object(
                    tarea_service.grupo_repository,
                    "obtener_integrante",
                    side_effect=_obtener_integrante,
                )
            )
            mocks["obtener_asignados"] = stack.enter_context(
                patch.object(
                    tarea_service.asignacion_tarea_repository,
                    "obtener_usuarios_asignados",
                    side_effect=_obtener_asignados,
                )
            )
            mocks["obtener_completados"] = stack.enter_context(
                patch.object(
                    tarea_service.historial_tarea_repository,
                    "obtener_usuarios_completados",
                    return_value=completados,
                )
            )
            mocks["obtener_fila"] = stack.enter_context(
                patch.object(
                    tarea_service.historial_tarea_repository,
                    "obtener_fila",
                    side_effect=_obtener_fila,
                )
            )
            mocks["obtener_archivos"] = stack.enter_context(
                patch.object(
                    tarea_service.archivo_repository,
                    "obtener_archivos_de_usuarios_en_tarea",
                    side_effect=_obtener_archivos,
                )
            )
            mocks["obtener_sesiones"] = stack.enter_context(
                patch.object(
                    tarea_service.sesion_cronometro_repository,
                    "obtener_sesiones_de_usuario_en_tarea",
                    side_effect=_obtener_sesiones,
                )
            )
            mocks["eliminar_archivos"] = stack.enter_context(
                patch.object(
                    tarea_service.archivo_repository,
                    "eliminar_archivos_de_usuarios_en_tarea",
                )
            )
            mocks["eliminar_sesiones"] = stack.enter_context(
                patch.object(
                    tarea_service.sesion_cronometro_repository,
                    "eliminar_sesiones_de_usuario_en_tarea",
                )
            )
            mocks["eliminar_historial"] = stack.enter_context(
                patch.object(
                    tarea_service.historial_tarea_repository,
                    "eliminar_por_usuario_y_tarea",
                )
            )
            mocks["eliminar_asignacion"] = stack.enter_context(
                patch.object(
                    tarea_service.asignacion_tarea_repository,
                    "eliminar_por_tarea_e_integrante",
                )
            )
            mocks["crear_asignacion"] = stack.enter_context(
                patch.object(
                    tarea_service.asignacion_tarea_repository,
                    "crear_asignacion",
                )
            )
            mocks["cuarentena"] = stack.enter_context(
                patch.object(
                    tarea_service.archivo_service,
                    "preparar_eliminacion_archivos_usuarios_tarea",
                    cuarentena or _cuarentena,
                )
            )
            mocks["contar_archivos"] = stack.enter_context(
                patch.object(
                    tarea_service.archivo_repository,
                    "contar_archivos_de_tarea",
                    return_value=0,
                )
            )
            mocks["notificar"] = stack.enter_context(
                patch.object(
                    tarea_service.notificacion_repository,
                    "crear_notificacion",
                )
            )
            resultado = tarea_service.reasignar_asignados_tarea(
                db, 4, ids_nuevos, 12
            )
        return resultado, db, mocks

    def test_lider_reasigna_y_actualiza_asignaciones(self):
        resultado, db, mocks = self._ejecutar(
            ids_nuevos=[12, 14],
            asignados_actuales=[12, 13],
            asignados_finales=[12, 14],
        )
        self.assertEqual(resultado.estado, "en progreso")
        db.commit.assert_called_once()
        mocks["eliminar_archivos"].assert_called_once_with(db, 4, [13])
        mocks["eliminar_sesiones"].assert_called_once_with(db, 4, 13)
        mocks["eliminar_historial"].assert_called_once_with(db, 4, 13)
        mocks["eliminar_asignacion"].assert_called_once_with(db, 4, 113)
        mocks["crear_asignacion"].assert_called_once_with(db, 4, 114, commit=False)

    def test_mismo_conjunto_no_cambia_ni_notifica(self):
        resultado, db, mocks = self._ejecutar(
            ids_nuevos=[12, 13],
            asignados_actuales=[12, 13],
            asignados_finales=[12, 13],
        )
        self.assertEqual(resultado.total_archivos, 0)
        db.commit.assert_not_called()
        mocks["crear_asignacion"].assert_not_called()
        mocks["eliminar_archivos"].assert_not_called()
        mocks["notificar"].assert_not_called()

    def test_quitado_con_trabajo_usa_detalle_de_archivos_y_tiempo(self):
        _, _, mocks = self._ejecutar(
            ids_nuevos=[12],
            asignados_actuales=[12, 13],
            asignados_finales=[12],
            archivos_por_usuario={13: [SimpleNamespace(id_archivo=1)]},
        )
        notificacion = next(
            llamada
            for llamada in mocks["notificar"].call_args_list
            if llamada.kwargs["id_usuario"] == 13
        )
        self.assertEqual(
            notificacion.kwargs["titulo"],
            "Ya no estás asignado a una tarea",
        )
        self.assertIn(
            "Se borraron tus archivos y tu tiempo.",
            notificacion.kwargs["detalles"],
        )
        self.assertEqual(notificacion.kwargs["tipo"], "tarea_retirada")

    def test_quitado_sin_trabajo_usa_detalle_corto(self):
        _, _, mocks = self._ejecutar(
            ids_nuevos=[12],
            asignados_actuales=[12, 13],
            asignados_finales=[12],
        )
        notificacion = next(
            llamada
            for llamada in mocks["notificar"].call_args_list
            if llamada.kwargs["id_usuario"] == 13
        )
        self.assertNotIn("Se borraron", notificacion.kwargs["detalles"])
        self.assertEqual(
            notificacion.kwargs["detalles"],
            "El líder te quitó de «Tarea de prueba».",
        )

    def test_notifica_al_nuevo_con_fecha_corta(self):
        _, _, mocks = self._ejecutar(
            ids_nuevos=[12, 14],
            asignados_actuales=[12, 13],
            asignados_finales=[12, 14],
        )
        notificacion = next(
            llamada
            for llamada in mocks["notificar"].call_args_list
            if llamada.kwargs["id_usuario"] == 14
        )
        self.assertEqual(notificacion.kwargs["titulo"], "Tienes una tarea nueva")
        self.assertEqual(
            notificacion.kwargs["detalles"],
            "El líder te asignó «Tarea de prueba». Entrega: 30 oct.",
        )
        self.assertEqual(notificacion.kwargs["tipo"], "tarea_asignada")

    def test_estado_completada_cuando_todos_los_nuevos_tienen_historial(self):
        resultado, _, _ = self._ejecutar(
            ids_nuevos=[12],
            asignados_actuales=[12, 13],
            asignados_finales=[12],
            completados={12},
        )
        self.assertEqual(resultado.estado, "Completada")

    def test_no_recalcula_estadistica(self):
        with patch(
            "app.services.estadistica_service.recalcular_estadistica_categoria"
        ) as recalcular:
            self._ejecutar(
                ids_nuevos=[12, 14],
                asignados_actuales=[12, 13],
                asignados_finales=[12, 14],
            )
        recalcular.assert_not_called()

    def test_nombre_largo_se_recorta_a_35_con_punto_suspensivo(self):
        nombre = "Tarea con un nombre realmente largo para notificar"
        _, _, mocks = self._ejecutar(
            ids_nuevos=[12, 14],
            asignados_actuales=[12, 13],
            asignados_finales=[12, 14],
            nombre=nombre,
        )
        detalle = mocks["notificar"].call_args_list[0].kwargs["detalles"]
        self.assertIn("…", detalle)
        self.assertNotIn(nombre, detalle)
        self.assertLessEqual(len(detalle), 100)

    def test_titulo_y_detalle_respetan_los_limites(self):
        _, _, mocks = self._ejecutar(
            ids_nuevos=[12, 14],
            asignados_actuales=[12, 13],
            asignados_finales=[12, 14],
        )
        for llamada in mocks["notificar"].call_args_list:
            self.assertLessEqual(len(llamada.kwargs["titulo"]), 50)
            self.assertLessEqual(len(llamada.kwargs["detalles"]), 100)

    def test_fallo_de_almacenamiento_no_rompe_la_reasignacion(self):
        @contextmanager
        def _cuarentena_con_fallo(_db, _id_tarea, _ids_usuarios):
            try:
                raise OSError("fallo de almacenamiento simulado")
            except OSError:
                pass
            yield

        resultado, db, _ = self._ejecutar(
            ids_nuevos=[12, 14],
            asignados_actuales=[12, 13],
            asignados_finales=[12, 14],
            cuarentena=_cuarentena_con_fallo,
        )
        self.assertEqual(resultado.estado, "en progreso")
        db.commit.assert_called_once()


class CuarentenaToleranteTests(unittest.TestCase):
    """El helper de C4c no debe lanzar si el almacenamiento falla."""

    def test_fallo_de_os_replace_no_lanza(self):
        with tempfile.TemporaryDirectory() as directorio:
            base = Path(directorio)
            carpeta = base / "4"
            carpeta.mkdir()
            (carpeta / "evidencia.pdf").write_bytes(b"%PDF-1.4 prueba")
            adjunto = SimpleNamespace(
                id_archivo=1, ruta="4/evidencia.pdf", tipo="PDF"
            )
            with (
                patch.object(
                    archivo_service.archivo_repository,
                    "obtener_archivos_de_usuarios_en_tarea",
                    return_value=[adjunto],
                ),
                patch.object(
                    archivo_service.archivo_repository,
                    "existe_referencia_fuera_de_tarea",
                    return_value=False,
                ),
                patch.object(archivo_service, "DIRECTORIO_BASE_UPLOADS", base),
                patch.object(
                    archivo_service, "DIRECTORIO_UPLOADS_HISTORICOS", base
                ),
                patch.object(
                    archivo_service.os,
                    "replace",
                    side_effect=OSError("fallo simulado"),
                ),
                self.assertLogs("app.services.archivo_service", level="ERROR"),
            ):
                with archivo_service.preparar_eliminacion_archivos_usuarios_tarea(
                    Mock(), 4, [13]
                ):
                    pass


class CrearTareaGrupalNotificacionTests(unittest.TestCase):
    def test_notifica_a_asignados_menos_al_lider(self):
        usuario = SimpleNamespace(id_usuario=12, es_admin=False)
        datos = tarea_service.TareaGrupalCreate(
            nombre="Tarea nueva",
            fecha_entrega=datetime(2026, 10, 30, 23, 59),
            dificultad_estimada=3,
            tiempo_estimado=30,
            id_categoria=1,
            ids_usuarios=[12, 13, 14],
        )
        integrantes = [
            SimpleNamespace(id_usuario=12, id_integrante=112, rol="lider"),
            SimpleNamespace(id_usuario=13, id_integrante=113, rol="miembro"),
            SimpleNamespace(id_usuario=14, id_integrante=114, rol="miembro"),
        ]
        tarea = SimpleNamespace(
            id_tarea=7,
            nombre="Tarea nueva",
            fecha_entrega=datetime(2026, 10, 30, 23, 59),
        )
        db = Mock()
        with (
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(
                tarea_service.grupo_repository,
                "obtener_integrante",
                side_effect=integrantes,
            ),
            patch.object(
                tarea_service.tarea_repository,
                "crear_tarea",
                return_value=tarea,
            ),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "crear_asignacion",
            ),
            patch.object(
                tarea_service.notificacion_repository,
                "crear_notificacion",
            ) as notificar,
        ):
            resultado = tarea_service.crear_tarea_grupal(db, 7, datos, usuario)

        self.assertIs(resultado, tarea)
        self.assertEqual(notificar.call_count, 2)
        destinatarios = {
            llamada.kwargs["id_usuario"] for llamada in notificar.call_args_list
        }
        self.assertEqual(destinatarios, {13, 14})
        for llamada in notificar.call_args_list:
            self.assertEqual(llamada.kwargs["titulo"], "Tienes una tarea nueva")
            self.assertEqual(llamada.kwargs["tipo"], "tarea_asignada")
            self.assertIn("30 oct.", llamada.kwargs["detalles"])


class FechaCortaTests(unittest.TestCase):
    def test_formatea_dia_y_mes_en_espanol(self):
        self.assertEqual(
            tarea_service._formatear_fecha_corta(datetime(2026, 10, 30, 23, 59)),
            "30 oct.",
        )

    def test_fecha_nula_devuelve_texto_vacio(self):
        self.assertEqual(tarea_service._formatear_fecha_corta(None), "")


if __name__ == "__main__":
    unittest.main()
