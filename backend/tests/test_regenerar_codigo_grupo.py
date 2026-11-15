# Ruta: backend/tests/test_regenerar_codigo_grupo.py
# Pruebas de C7: POST /grupos/{id_grupo}/regenerar-codigo
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLSession

from app.api.v1.endpoints import grupos as endpoints
from app.db.base import Base
from app.dependencies.auth import requerir_lider_de_grupo
from app.models.grupo import Grupo
from app.models.integrante import Integrante
from app.models.usuario import Usuario
from app.services import grupo_service


class RegenerarCodigoBase(unittest.TestCase):
    """Base con SQLite en memoria: un grupo con líder y miembro."""

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(
            self.engine,
            tables=[Usuario.__table__, Grupo.__table__, Integrante.__table__],
        )
        self.db = SQLSession(self.engine)
        self.db.add_all(
            [
                Usuario(id_usuario=1, correo_electronico="lider@example.test", contrasena="hash"),
                Usuario(id_usuario=2, correo_electronico="miembro@example.test", contrasena="hash"),
                Usuario(id_usuario=3, correo_electronico="nuevo@example.test", contrasena="hash"),
            ]
        )
        self.db.flush()
        self.db.add_all(
            [
                Grupo(id_grupo=10, nombre_grupo="Grupo propio", codigo_acceso="VIEJO123"),
                Grupo(id_grupo=11, nombre_grupo="Grupo ajeno", codigo_acceso="OTRO1234"),
            ]
        )
        self.db.flush()
        self.db.add_all(
            [
                Integrante(id_usuario=1, id_grupo=10, rol="lider"),
                Integrante(id_usuario=2, id_grupo=10, rol="miembro"),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()


class RegenerarCodigoExitosoTests(RegenerarCodigoBase):
    def test_lider_regenera_y_el_codigo_cambia(self):
        grupo = grupo_service.regenerar_codigo_acceso(self.db, 10)

        self.assertNotEqual(grupo.codigo_acceso, "VIEJO123")
        self.assertEqual(len(grupo.codigo_acceso), 8)

    def test_codigo_viejo_ya_no_sirve_y_el_nuevo_si(self):
        grupo = grupo_service.regenerar_codigo_acceso(self.db, 10)
        nuevo_codigo = grupo.codigo_acceso

        with self.assertRaises(HTTPException) as error:
            grupo_service.unirse_a_grupo(self.db, "VIEJO123", 3)
        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, "Código de acceso inválido")

        integrante = grupo_service.unirse_a_grupo(self.db, nuevo_codigo, 3)
        self.assertEqual(integrante.id_grupo, 10)
        self.assertEqual(integrante.id_usuario, 3)

    def test_integrantes_actuales_siguen_en_el_grupo(self):
        antes = grupo_service.listar_integrantes_de_grupo(self.db, 10, 1)

        grupo_service.regenerar_codigo_acceso(self.db, 10)

        despues = grupo_service.listar_integrantes_de_grupo(self.db, 10, 1)
        self.assertEqual(len(despues), len(antes))
        self.assertEqual({i["id_usuario"] for i in despues}, {1, 2})

    def test_codigo_nuevo_es_unico_en_la_base(self):
        grupo = grupo_service.regenerar_codigo_acceso(self.db, 10)

        otro = (
            self.db.query(Grupo)
            .filter(Grupo.codigo_acceso == grupo.codigo_acceso, Grupo.id_grupo != 10)
            .first()
        )
        self.assertIsNone(otro)


class RegenerarCodigoErroresTests(RegenerarCodigoBase):
    def test_grupo_inexistente_devuelve_404(self):
        with self.assertRaises(HTTPException) as error:
            grupo_service.regenerar_codigo_acceso(self.db, 999)

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, "Grupo no encontrado")

    def test_miembro_no_lider_recibe_403(self):
        miembro = SimpleNamespace(id_usuario=2, es_admin=False)

        with self.assertRaises(HTTPException) as error:
            requerir_lider_de_grupo(id_grupo=10, usuario=miembro, db=self.db)

        self.assertEqual(error.exception.status_code, 403)

    def test_usuario_ajeno_al_grupo_recibe_403(self):
        ajeno = SimpleNamespace(id_usuario=3, es_admin=False)

        with self.assertRaises(HTTPException) as error:
            requerir_lider_de_grupo(id_grupo=10, usuario=ajeno, db=self.db)

        self.assertEqual(error.exception.status_code, 403)


class RegenerarCodigoEndpointTests(unittest.TestCase):
    def test_endpoint_delega_en_el_service(self):
        usuario_actual = SimpleNamespace(id_usuario=1)
        grupo = SimpleNamespace(
            id_grupo=10,
            nombre_grupo="Grupo propio",
            descripcion=None,
            codigo_acceso="NUEVO123",
            fecha_creacion=None,
        )
        with patch.object(
            endpoints.grupo_service, "regenerar_codigo_acceso", return_value=grupo
        ) as regenerar:
            resultado = endpoints.regenerar_codigo_acceso(10, None, usuario_actual)

        regenerar.assert_called_once_with(None, 10)
        self.assertIs(resultado, grupo)


if __name__ == "__main__":
    unittest.main()
