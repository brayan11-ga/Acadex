import io
import tempfile
import unittest
import zipfile
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from app.services import archivo_service, tarea_service


def crear_upload(nombre: str, contenido: bytes, mime: str) -> UploadFile:
    return UploadFile(
        file=io.BytesIO(contenido),
        filename=nombre,
        headers=Headers({"content-type": mime}),
    )


def crear_docx() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as documento:
        documento.writestr("[Content_Types].xml", "<Types/>")
        documento.writestr("word/document.xml", "<document/>")
    return buffer.getvalue()


class ValidacionArchivoTests(unittest.TestCase):
    def test_conserva_formatos_admitidos(self):
        ejemplos = [
            ("guia.pdf", b"%PDF-1.7\ncontenido", "application/pdf", "PDF"),
            (
                "guia.docx",
                crear_docx(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "DOCX",
            ),
            ("foto.jpg", b"\xff\xd8\xff\xe0contenido", "image/jpeg", "JPG"),
            ("foto.jpeg", b"\xff\xd8\xff\xe0contenido", "image/jpeg", "JPG"),
            ("foto.png", b"\x89PNG\r\n\x1a\ncontenido", "image/png", "PNG"),
        ]

        for nombre, contenido, mime, tipo_esperado in ejemplos:
            with self.subTest(nombre=nombre):
                validado = archivo_service._validar_archivo(crear_upload(nombre, contenido, mime))
                self.assertEqual(validado[0], nombre)
                self.assertEqual(validado[1], tipo_esperado)

    def test_rechaza_extension_fuera_de_la_politica_actual(self):
        for nombre in ("trabajo.doc", "script.exe"):
            with self.subTest(nombre=nombre), self.assertRaises(HTTPException) as error:
                archivo_service._validar_archivo(crear_upload(nombre, b"contenido", "application/octet-stream"))
            self.assertEqual(error.exception.status_code, 415)

    def test_rechaza_mime_o_firma_incompatibles(self):
        casos = [
            crear_upload("falso.pdf", b"no es pdf", "application/pdf"),
            crear_upload("foto.png", b"texto", "image/png"),
            crear_upload("foto.jpg", b"\x89PNG\r\n\x1a\n", "image/jpeg"),
        ]
        for archivo in casos:
            with self.subTest(nombre=archivo.filename), self.assertRaises(HTTPException) as error:
                archivo_service._validar_archivo(archivo)
            self.assertEqual(error.exception.status_code, 415)

    def test_rechaza_archivos_vacios_y_mayores_a_cinco_mib(self):
        with self.assertRaises(HTTPException) as vacio:
            archivo_service._validar_archivo(crear_upload("vacio.pdf", b"", "application/pdf"))
        self.assertEqual(vacio.exception.status_code, 400)

        contenido_grande = b"%PDF-" + b"x" * (archivo_service.TAMANO_MAXIMO_BYTES + 1)
        with self.assertRaises(HTTPException) as grande:
            archivo_service._validar_archivo(crear_upload("grande.pdf", contenido_grande, "application/pdf"))
        self.assertEqual(grande.exception.status_code, 413)

    def test_rechaza_rutas_guardadas_con_traversal(self):
        with self.assertRaises(ValueError):
            archivo_service._resolver_ruta("../secreto.txt")
        with self.assertRaises(ValueError):
            archivo_service._resolver_ruta("5/guia.pdf", id_tarea_esperada=4)

    def test_normaliza_nombre_sin_conservar_directorios(self):
        self.assertEqual(archivo_service._normalizar_nombre("..\\privado\\guia.pdf"), "guia.pdf")


class AutorizacionAdjuntosTests(unittest.TestCase):
    @patch.object(archivo_service.asignacion_tarea_repository, "usuario_tiene_asignacion")
    @patch.object(archivo_service.tarea_repository, "obtener_tarea_por_id")
    def test_solo_propietario_accede_a_tarea_personal(self, obtener_tarea, asignado):
        tarea = SimpleNamespace(id_usuario=12, id_grupo=None)
        obtener_tarea.return_value = tarea

        self.assertIs(archivo_service._autorizacion_tarea(None, 5, 12), tarea)
        asignado.assert_not_called()

        with self.assertRaises(HTTPException) as error:
            archivo_service._autorizacion_tarea(None, 5, 13)
        self.assertEqual(error.exception.status_code, 403)

    def test_una_tarea_inexistente_no_autoriza(self):
        with patch.object(archivo_service.tarea_repository, "obtener_tarea_por_id", return_value=None):
            with self.assertRaises(HTTPException) as error:
                archivo_service._autorizacion_tarea(None, 404, 12)
        self.assertEqual(error.exception.status_code, 404)

    @patch.object(archivo_service.asignacion_tarea_repository, "usuario_tiene_asignacion")
    @patch.object(archivo_service.tarea_repository, "obtener_tarea_por_id")
    def test_tarea_grupal_requiere_asignacion_directa(self, obtener_tarea, asignado):
        tarea = SimpleNamespace(id_usuario=None, id_grupo=7)
        obtener_tarea.return_value = tarea
        asignado.return_value = True
        self.assertIs(archivo_service._autorizacion_tarea(None, 5, 12), tarea)

        asignado.return_value = False
        with self.assertRaises(HTTPException) as error:
            archivo_service._autorizacion_tarea(None, 5, 13)
        self.assertEqual(error.exception.status_code, 403)


class ConsistenciaAlmacenamientoTests(unittest.TestCase):
    def test_borrado_fallido_restaurar_archivo(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directorio:
            original = Path(directorio) / "entrega.pdf"
            original.write_bytes(b"contenido")

            with self.assertRaises(RuntimeError):
                with archivo_service._archivos_en_cuarentena([original]):
                    self.assertFalse(original.exists())
                    raise RuntimeError("fallo simulado de base de datos")

            self.assertEqual(original.read_bytes(), b"contenido")

    def test_borrado_confirmado_retira_archivo(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directorio:
            original = Path(directorio) / "entrega.pdf"
            original.write_bytes(b"contenido")

            with archivo_service._archivos_en_cuarentena([original]):
                self.assertFalse(original.exists())

            self.assertFalse(original.exists())


class FlujoAdjuntosTests(unittest.TestCase):
    @staticmethod
    def archivo_falso(ruta: str, *, autor: int | None = 12, id_tarea: int = 4):
        return SimpleNamespace(
            id_archivo=8,
            nombre="guia.pdf",
            tamano=13,
            tipo="PDF",
            fecha_adjuncion=datetime(2026, 10, 11),
            ruta=ruta,
            id_tarea=id_tarea,
            id_usuario_subida=autor,
        )

    def test_subida_personal_guarda_autor_y_no_expone_ruta(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directorio:
            raiz = Path(directorio)
            tarea = SimpleNamespace(id_usuario=12, id_grupo=None, nombre="Lectura")
            with (
                patch.object(archivo_service, "DIRECTORIO_BASE_UPLOADS", raiz),
                patch.object(archivo_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea),
                patch.object(
                    archivo_service.archivo_repository,
                    "crear_archivo",
                    side_effect=lambda _db, **datos: self.archivo_falso(
                        datos["ruta"], autor=datos["id_usuario_subida"], id_tarea=datos["id_tarea"]
                    ),
                ) as crear,
            ):
                respuesta = archivo_service.subir_archivo_tarea(
                    None,
                    4,
                    crear_upload("guia.pdf", b"%PDF-1.7 test", "application/pdf"),
                    12,
                )

            self.assertEqual(crear.call_args.kwargs["id_usuario_subida"], 12)
            ruta_guardada = crear.call_args.kwargs["ruta"]
            self.assertTrue((raiz / ruta_guardada).is_file())
            self.assertNotIn("guia.pdf", ruta_guardada)
            self.assertTrue(respuesta["puede_eliminar"])
            self.assertNotIn("ruta", respuesta)

    def test_fallo_al_guardar_metadatos_compensa_el_binario(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directorio:
            raiz = Path(directorio)
            tarea = SimpleNamespace(id_usuario=12, id_grupo=None, nombre="Lectura")
            db = Mock()
            with (
                patch.object(archivo_service, "DIRECTORIO_BASE_UPLOADS", raiz),
                patch.object(archivo_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea),
                patch.object(archivo_service.archivo_repository, "crear_archivo", side_effect=RuntimeError("db")),
            ):
                with patch.object(archivo_service.logger, "exception"):
                    with self.assertRaises(HTTPException) as error:
                        archivo_service.subir_archivo_tarea(
                            db,
                            4,
                            crear_upload("guia.pdf", b"%PDF-1.7 test", "application/pdf"),
                            12,
                        )

            self.assertEqual(error.exception.status_code, 500)
            self.assertEqual(list(raiz.rglob("*.pdf")), [])
            db.rollback.assert_called_once()

    def test_descarga_exige_que_el_archivo_pertenezca_a_la_tarea(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directorio:
            raiz = Path(directorio)
            binario = raiz / "4" / "guia.pdf"
            binario.parent.mkdir()
            binario.write_bytes(b"%PDF-1.7 test")
            tarea = SimpleNamespace(id_usuario=12, id_grupo=None)
            archivo = self.archivo_falso("4/guia.pdf")

            with (
                patch.object(archivo_service, "DIRECTORIO_BASE_UPLOADS", raiz),
                patch.object(archivo_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea),
                patch.object(archivo_service.archivo_repository, "obtener_archivo_de_tarea", return_value=archivo),
            ):
                archivo_devuelto, ruta = archivo_service.obtener_archivo_para_descarga(None, 4, 8, 12)
                self.assertIs(archivo_devuelto, archivo)
                self.assertEqual(ruta, binario.resolve())

                with patch.object(
                    archivo_service.archivo_repository,
                    "obtener_archivo_de_tarea",
                    return_value=None,
                ):
                    with self.assertRaises(HTTPException) as error:
                        archivo_service.obtener_archivo_para_descarga(None, 5, 8, 12)
                self.assertEqual(error.exception.status_code, 404)

    def test_borrar_adjuntos_compensa_si_falla_el_commit(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as directorio:
            raiz = Path(directorio)
            binario = raiz / "4" / "guia.pdf"
            binario.parent.mkdir()
            binario.write_bytes(b"%PDF-1.7 test")
            tarea = SimpleNamespace(id_usuario=12, id_grupo=None)
            archivo = self.archivo_falso("4/guia.pdf")
            db = Mock()

            with (
                patch.object(archivo_service, "DIRECTORIO_BASE_UPLOADS", raiz),
                patch.object(archivo_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea),
                patch.object(
                    archivo_service.archivo_repository,
                    "obtener_archivo_de_tarea",
                    return_value=archivo,
                ),
                patch.object(
                    archivo_service.archivo_repository,
                    "existe_otra_referencia_a_ruta",
                    return_value=False,
                ),
                patch.object(archivo_service.archivo_repository, "eliminar_archivo", side_effect=RuntimeError("db")),
            ):
                with self.assertRaises(HTTPException) as error:
                    archivo_service.eliminar_archivo_tarea(db, 4, 8, 12)

            self.assertEqual(error.exception.status_code, 500)
            self.assertEqual(binario.read_bytes(), b"%PDF-1.7 test")
            db.rollback.assert_called_once()

    def test_asignado_grupal_no_puede_borrar_adjunto_de_otro(self):
        tarea = SimpleNamespace(id_usuario=None, id_grupo=7)
        archivo = self.archivo_falso("7/guia.pdf", autor=12, id_tarea=7)
        with (
            patch.object(archivo_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea),
            patch.object(archivo_service.asignacion_tarea_repository, "usuario_tiene_asignacion", return_value=True),
            patch.object(archivo_service.archivo_repository, "obtener_archivo_de_tarea", return_value=archivo),
            patch.object(archivo_service.archivo_repository, "eliminar_archivo") as eliminar,
        ):
            with self.assertRaises(HTTPException) as error:
                archivo_service.eliminar_archivo_tarea(None, 7, 8, 13)

        self.assertEqual(error.exception.status_code, 403)
        eliminar.assert_not_called()


class EliminacionTareaTests(unittest.TestCase):
    def test_solo_propietario_elimina_tarea_personal(self):
        tarea = SimpleNamespace(id_usuario=12, id_grupo=None)
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(archivo_service, "preparar_eliminacion_archivos_tarea", return_value=nullcontext()),
            patch.object(tarea_service.tarea_repository, "eliminar_tarea") as eliminar,
        ):
            tarea_service.eliminar_tarea(None, 4, 12)
            eliminar.assert_called_once_with(None, tarea)

            with self.assertRaises(HTTPException) as error:
                tarea_service.eliminar_tarea(None, 4, 13)

        self.assertEqual(error.exception.status_code, 403)
        self.assertEqual(eliminar.call_count, 1)

    def test_lider_del_grupo_puede_eliminar_tarea_grupal(self):
        tarea = SimpleNamespace(id_usuario=None, id_grupo=7)
        lider = SimpleNamespace(rol="lider")
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service.grupo_repository, "obtener_integrante", return_value=lider),
            patch.object(archivo_service, "preparar_eliminacion_archivos_tarea", return_value=nullcontext()),
            patch.object(tarea_service.tarea_repository, "eliminar_tarea") as eliminar,
        ):
            tarea_service.eliminar_tarea(None, 7, 12)
        eliminar.assert_called_once_with(None, tarea)


if __name__ == "__main__":
    unittest.main()
