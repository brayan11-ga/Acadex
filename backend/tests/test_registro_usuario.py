import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from app.core.legal import VERSION_AVISO_ALMACENAMIENTO, VERSION_POLITICA_DATOS
from app.api.v1.endpoints import usuarios as usuarios_endpoint
from app.models.consentimiento_usuario import ConsentimientoUsuario
from app.schemas.usuario import UsuarioCreate
from app.services import usuario_service


class RegistroUsuarioTests(unittest.TestCase):
    def datos_registro(self, **cambios):
        return {
            "correo_electronico": "persona@example.com",
            "nombre_usuario": "  Nombre de prueba  ",
            "contrasena": "ClaveSegura123",
            "acepta_tratamiento_datos": True,
            "confirma_aviso_almacenamiento": True,
            **cambios,
        }

    def test_esquema_normaliza_nombre_y_respeta_limite_del_perfil(self):
        datos = UsuarioCreate(**self.datos_registro())
        self.assertEqual(datos.nombre_usuario, "Nombre de prueba")
        datos_compatibles = self.datos_registro()
        datos_compatibles.pop("nombre_usuario")
        self.assertIsNone(UsuarioCreate(**datos_compatibles).nombre_usuario)

        for valor in ("   ", "x" * 51):
            with self.subTest(nombre=valor), self.assertRaises(ValidationError):
                UsuarioCreate(**self.datos_registro(nombre_usuario=valor))

    @patch.object(usuarios_endpoint, "registrar_intento")
    @patch.object(usuarios_endpoint.service, "registrar_usuario")
    def test_endpoint_envia_el_nombre_y_las_dos_confirmaciones_al_servicio(
        self, registrar, _intento
    ):
        datos = UsuarioCreate(**self.datos_registro())
        request = SimpleNamespace(client=SimpleNamespace(host="cliente-sintetico"))
        db = Mock()

        usuarios_endpoint.crear_usuario(datos, request, db)

        registrar.assert_called_once_with(
            db,
            "persona@example.com",
            "ClaveSegura123",
            True,
            True,
            nombre_usuario="Nombre de prueba",
        )

    def test_rechaza_confirmacion_falsa_antes_de_escribir(self):
        db = Mock()

        with self.assertRaises(HTTPException) as error:
            usuario_service.registrar_usuario(
                db,
                "persona@example.com",
                "ClaveSegura123",
                True,
                False,
                nombre_usuario="Nombre",
            )

        self.assertEqual(error.exception.status_code, 422)
        db.commit.assert_not_called()
        db.add_all.assert_not_called()

    @patch.object(usuario_service, "hash_password", return_value="hash-sintetico")
    @patch.object(usuario_service.perfil_repo, "create_perfil")
    @patch.object(usuario_service.repo, "create_usuario", return_value=SimpleNamespace(id_usuario=26))
    @patch.object(usuario_service.repo, "get_usuario_by_correo", return_value=None)
    def test_cliente_que_omite_nombre_conserva_el_nombre_por_defecto_anterior(
        self, _buscar, _crear_usuario, crear_perfil, _hash
    ):
        db = Mock()

        usuario_service.registrar_usuario(
            db, "persona@example.com", "ClaveSegura123", True, True
        )

        self.assertEqual(
            crear_perfil.call_args.args[1]["nombre_usuario"], "persona"
        )

    @patch.object(usuario_service, "hash_password", return_value="hash-sintetico")
    @patch.object(usuario_service.perfil_repo, "create_perfil")
    @patch.object(usuario_service.repo, "create_usuario")
    @patch.object(usuario_service.repo, "get_usuario_by_correo", return_value=None)
    def test_persiste_nombre_y_dos_evidencias_con_versiones_configuradas(
        self, _buscar, crear_usuario, crear_perfil, _hash
    ):
        db = Mock()
        usuario = SimpleNamespace(id_usuario=27)
        crear_usuario.return_value = usuario

        resultado = usuario_service.registrar_usuario(
            db,
            "persona@example.com",
            "ClaveSegura123",
            True,
            True,
            nombre_usuario="Nombre de prueba",
        )

        self.assertIs(resultado, usuario)
        crear_perfil.assert_called_once_with(
            db,
            {"id_usuario": 27, "nombre_usuario": "Nombre de prueba"},
            commit=False,
        )
        evidencias = db.add_all.call_args.args[0]
        self.assertEqual(len(evidencias), 2)
        self.assertTrue(all(isinstance(item, ConsentimientoUsuario) for item in evidencias))
        self.assertEqual(
            {(item.tipo_consentimiento, item.version_politica) for item in evidencias},
            {
                ("tratamiento_datos", VERSION_POLITICA_DATOS),
                ("aviso_almacenamiento", VERSION_AVISO_ALMACENAMIENTO),
            },
        )
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(usuario)

    @patch.object(usuario_service, "hash_password", return_value="hash-sintetico")
    @patch.object(usuario_service.perfil_repo, "create_perfil")
    @patch.object(usuario_service.repo, "create_usuario", return_value=SimpleNamespace(id_usuario=28))
    @patch.object(usuario_service.repo, "get_usuario_by_correo", return_value=None)
    def test_revierte_si_falla_la_confirmacion_de_la_transaccion(
        self, _buscar, _crear_usuario, _crear_perfil, _hash
    ):
        db = Mock()
        db.commit.side_effect = RuntimeError("fallo de persistencia simulado")

        with self.assertRaisesRegex(RuntimeError, "fallo de persistencia"):
            usuario_service.registrar_usuario(
                db,
                "persona@example.com",
                "ClaveSegura123",
                True,
                True,
                nombre_usuario="Nombre",
            )

        db.rollback.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
