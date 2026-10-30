# Ruta: backend/tests/test_limite_archivos.py
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.tarea import TareaResponse
from app.services import archivo_service, tarea_service


class LimiteAlSubirArchivoTests(unittest.TestCase):
    """Escenarios de subida: dentro del límite y al alcanzar el máximo (409)."""

    def test_subir_archivo_dentro_del_limite_continua(self):
        tarea = SimpleNamespace(max_archivos=2)
        centinela = HTTPException(status_code=415, detail="validación alcanzada")
        with (
            patch.object(archivo_service, "_exigir_adjuntos_habilitados"),
            patch.object(archivo_service, "_autorizacion_tarea", return_value=tarea),
            patch.object(
                archivo_service.archivo_repository,
                "contar_archivos_de_tarea",
                return_value=1,
            ),
            patch.object(archivo_service, "_validar_archivo", side_effect=centinela) as validar,
        ):
            with self.assertRaises(HTTPException) as error:
                archivo_service.subir_archivo_tarea(None, 4, Mock(), 12)
        # Llegó a _validar_archivo: el límite no lo detuvo.
        self.assertEqual(error.exception.status_code, 415)
        validar.assert_called_once()

    def test_subir_archivo_al_alcanzar_el_maximo_devuelve_409(self):
        tarea = SimpleNamespace(max_archivos=2)
        with (
            patch.object(archivo_service, "_exigir_adjuntos_habilitados"),
            patch.object(archivo_service, "_autorizacion_tarea", return_value=tarea),
            patch.object(
                archivo_service.archivo_repository,
                "contar_archivos_de_tarea",
                return_value=2,
            ),
            patch.object(archivo_service, "_validar_archivo") as validar,
        ):
            with self.assertRaises(HTTPException) as error:
                archivo_service.subir_archivo_tarea(None, 4, Mock(), 12)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(
            error.exception.detail, "Esta tarea ya alcanzó el máximo de 2 archivos."
        )
        validar.assert_not_called()


class LimiteAlActualizarTareaTests(unittest.TestCase):
    """Escenarios de PUT: líder sube el límite, tope del sistema y permisos."""

    def test_lider_puede_subir_el_maximo(self):
        tarea = SimpleNamespace(id_tarea=4, id_usuario=None, id_grupo=7, estado="Pendiente")
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(
                tarea_service.archivo_repository,
                "contar_archivos_de_tarea",
                return_value=1,
            ),
            patch.object(
                tarea_service.tarea_repository, "actualizar_tarea", return_value=tarea
            ) as actualizar,
        ):
            tarea_service.actualizar_tarea(
                None, 4, tarea_service.TareaUpdate(max_archivos=5), 12
            )
        actualizar.assert_called_once()

    def test_no_se_puede_superar_el_tope_del_sistema(self):
        tarea = SimpleNamespace(id_tarea=4, id_usuario=None, id_grupo=7, estado="Pendiente")
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(
                tarea_service.archivo_repository, "contar_archivos_de_tarea", return_value=0
            ),
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.actualizar_tarea(
                    None, 4, tarea_service.TareaUpdate(max_archivos=11), 12
                )
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "El máximo permitido por el sistema es 10.")

    def test_no_se_puede_bajar_el_maximo_bajo_los_archivos_existentes(self):
        tarea = SimpleNamespace(id_tarea=4, id_usuario=None, id_grupo=7, estado="Pendiente")
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(
                tarea_service.archivo_repository, "contar_archivos_de_tarea", return_value=3
            ),
            patch.object(tarea_service.tarea_repository, "actualizar_tarea") as actualizar,
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.actualizar_tarea(
                    None, 4, tarea_service.TareaUpdate(max_archivos=2), 12
                )
        self.assertEqual(error.exception.status_code, 400)
        self.assertIn("ya tiene 3 archivos", error.exception.detail)
        actualizar.assert_not_called()

    def test_miembro_no_lider_no_puede_cambiar_el_maximo(self):
        tarea = SimpleNamespace(id_tarea=4, id_usuario=None, id_grupo=7, estado="Pendiente")
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service, "_es_lider", return_value=False),
            patch.object(
                tarea_service.asignacion_tarea_repository,
                "usuario_tiene_asignacion",
                return_value=True,
            ),
            patch.object(
                tarea_service.archivo_repository, "contar_archivos_de_tarea"
            ) as contar,
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.actualizar_tarea(
                    None, 4, tarea_service.TareaUpdate(max_archivos=5), 12
                )
        self.assertEqual(error.exception.status_code, 403)
        contar.assert_not_called()

    def test_tarea_individual_rechaza_max_archivos(self):
        tarea = SimpleNamespace(id_tarea=4, id_usuario=12, id_grupo=None, estado="Pendiente")
        with patch.object(tarea_service, "obtener_tarea", return_value=tarea):
            with self.assertRaises(HTTPException) as error:
                tarea_service.actualizar_tarea(
                    None, 4, tarea_service.TareaUpdate(max_archivos=5), 12
                )
        self.assertEqual(error.exception.status_code, 400)


class LimiteAlCrearTareaGrupalTests(unittest.TestCase):
    def test_crear_grupal_sin_max_archivos_usa_tres(self):
        datos = tarea_service.TareaGrupalCreate(
            nombre="Tarea",
            fecha_entrega="2026-10-20T12:00:00",
            dificultad_estimada=3,
            tiempo_estimado=30,
            id_categoria=1,
            ids_usuarios=[13],
        )
        self.assertEqual(datos.max_archivos, 3)

    def test_crear_grupal_rechaza_max_archivos_mayor_al_tope(self):
        with self.assertRaises(ValidationError):
            tarea_service.TareaGrupalCreate(
                nombre="Tarea",
                fecha_entrega="2026-10-20T12:00:00",
                dificultad_estimada=3,
                tiempo_estimado=30,
                id_categoria=1,
                ids_usuarios=[13],
                max_archivos=11,
            )


class TotalArchivosEnRespuestaTests(unittest.TestCase):
    def test_adjuntar_total_archivos_usa_una_sola_consulta(self):
        tareas = [SimpleNamespace(id_tarea=4), SimpleNamespace(id_tarea=5)]
        with patch.object(
            tarea_service.archivo_repository,
            "obtener_conteo_archivos_por_tareas",
            return_value={4: 2},
        ) as contar:
            resultado = tarea_service._adjuntar_total_archivos(Mock(), tareas)
        self.assertEqual(resultado[0].total_archivos, 2)
        self.assertEqual(resultado[1].total_archivos, 0)
        contar.assert_called_once()

    def test_respuesta_incluye_max_y_total_archivos(self):
        tarea = SimpleNamespace(
            id_tarea=4,
            nombre="Tarea",
            descripcion=None,
            fecha_entrega=datetime(2026, 10, 20, 12, 0, 0),
            dificultad_estimada=3,
            tiempo_estimado=30,
            prioridad=None,
            id_categoria=1,
            estado="Pendiente",
            tiempo_acumulado=0.0,
            cronometro_activo=False,
            id_usuario=None,
            id_grupo=7,
            max_archivos=5,
            total_archivos=2,
        )
        respuesta = TareaResponse.model_validate(tarea)
        self.assertEqual(respuesta.max_archivos, 5)
        self.assertEqual(respuesta.total_archivos, 2)


if __name__ == "__main__":
    unittest.main()
