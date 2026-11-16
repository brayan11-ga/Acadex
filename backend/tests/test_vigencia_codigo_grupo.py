# Ruta: backend/tests/test_vigencia_codigo_grupo.py
# Pruebas de C7b: vigencia de 30 minutos del código de acceso del grupo.
import unittest
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLSession

from app.db.base import Base
from app.models.grupo import Grupo
from app.models.integrante import Integrante
from app.models.usuario import Usuario
from app.services import grupo_service


def _ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _vigente():
    return _ahora() + timedelta(minutes=30)


def _vencido():
    return datetime(2020, 1, 1, 12, 0, 0)


class VigenciaBase(unittest.TestCase):
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
                Usuario(
                    id_usuario=4,
                    correo_electronico="admin@example.test",
                    contrasena="hash",
                    es_admin=True,
                ),
            ]
        )
        self.db.flush()
        self.db.add_all(
            [
                Grupo(
                    id_grupo=10,
                    nombre_grupo="Vigente",
                    codigo_acceso="VIGENTE1",
                    fecha_expiracion_codigo=_vigente(),
                ),
                Grupo(
                    id_grupo=11,
                    nombre_grupo="Vencido",
                    codigo_acceso="VENCIDO1",
                    fecha_expiracion_codigo=_vencido(),
                ),
                Grupo(
                    id_grupo=12,
                    nombre_grupo="Sin fecha",
                    codigo_acceso="SINFECHA",
                    fecha_expiracion_codigo=None,
                ),
            ]
        )
        self.db.flush()
        self.db.add_all(
            [
                Integrante(id_usuario=1, id_grupo=10, rol="lider"),
                Integrante(id_usuario=2, id_grupo=10, rol="miembro"),
                # El admin también es miembro (no líder) del grupo 10.
                Integrante(id_usuario=4, id_grupo=10, rol="miembro"),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()


class CreacionYRegeneracionTests(VigenciaBase):
    def test_grupo_nuevo_vence_en_30_minutos(self):
        antes = _ahora()
        grupo = grupo_service.crear_grupo(self.db, "Nuevo", None, 1)
        despues = _ahora()

        self.assertEqual(len(grupo.codigo_acceso), 8)
        self.assertGreaterEqual(
            grupo.fecha_expiracion_codigo, antes + timedelta(minutes=30)
        )
        self.assertLessEqual(
            grupo.fecha_expiracion_codigo, despues + timedelta(minutes=30)
        )

    def test_regenerar_cambia_codigo_y_reinicia_vencimiento(self):
        grupo = self.db.get(Grupo, 10)
        codigo_viejo = grupo.codigo_acceso
        grupo.fecha_expiracion_codigo = _vencido()
        self.db.commit()

        antes = _ahora()
        regenerado = grupo_service.regenerar_codigo_acceso(self.db, 10)
        despues = _ahora()

        self.assertNotEqual(regenerado.codigo_acceso, codigo_viejo)
        self.assertGreaterEqual(
            regenerado.fecha_expiracion_codigo, antes + timedelta(minutes=30)
        )
        self.assertLessEqual(
            regenerado.fecha_expiracion_codigo, despues + timedelta(minutes=30)
        )


class UnionPorCodigoTests(VigenciaBase):
    def test_codigo_vigente_permite_unirse(self):
        integrante = grupo_service.unirse_a_grupo(self.db, "VIGENTE1", 3)

        self.assertEqual(integrante.id_grupo, 10)
        self.assertEqual(integrante.id_usuario, 3)
        self.assertEqual(integrante.rol, "miembro")

    def test_codigo_vencido_da_codigo_vencido(self):
        with self.assertRaises(HTTPException) as error:
            grupo_service.unirse_a_grupo(self.db, "VENCIDO1", 3)

        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(error.exception.detail, "Código vencido")

    def test_codigo_sin_fecha_da_codigo_vencido(self):
        with self.assertRaises(HTTPException) as error:
            grupo_service.unirse_a_grupo(self.db, "SINFECHA", 3)

        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(error.exception.detail, "Código vencido")

    def test_codigo_inexistente_da_invalido(self):
        with self.assertRaises(HTTPException) as error:
            grupo_service.unirse_a_grupo(self.db, "NOEXISTE", 3)

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, "Código de acceso inválido")

    def test_ya_integrante_no_se_agrega(self):
        with self.assertRaises(HTTPException) as error:
            grupo_service.unirse_a_grupo(self.db, "VIGENTE1", 2)

        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(error.exception.detail, "Ya perteneces a este grupo")
        self.assertEqual(
            self.db.query(Integrante)
            .filter(Integrante.id_usuario == 2, Integrante.id_grupo == 10)
            .count(),
            1,
        )

    def test_vencido_gana_a_ya_integrante(self):
        self.db.add(Integrante(id_usuario=3, id_grupo=11, rol="miembro"))
        self.db.commit()

        with self.assertRaises(HTTPException) as error:
            grupo_service.unirse_a_grupo(self.db, "VENCIDO1", 3)

        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(error.exception.detail, "Código vencido")

    def test_orden_inexistente_luego_vencido_luego_ya_integrante(self):
        with self.assertRaises(HTTPException) as inexistente:
            grupo_service.unirse_a_grupo(self.db, "NOEXISTE", 2)
        self.assertEqual(inexistente.exception.status_code, 404)
        self.assertEqual(inexistente.exception.detail, "Código de acceso inválido")

        with self.assertRaises(HTTPException) as vencido:
            grupo_service.unirse_a_grupo(self.db, "VENCIDO1", 2)
        self.assertEqual(vencido.exception.status_code, 409)
        self.assertEqual(vencido.exception.detail, "Código vencido")

        with self.assertRaises(HTTPException) as ya:
            grupo_service.unirse_a_grupo(self.db, "VIGENTE1", 2)
        self.assertEqual(ya.exception.status_code, 409)
        self.assertEqual(ya.exception.detail, "Ya perteneces a este grupo")


class VisibilidadCodigoTests(VigenciaBase):
    def test_lider_ve_codigo_y_fecha(self):
        filas = grupo_service.listar_grupos_de_usuario(self.db, 1, es_admin=False)
        fila = next(f for f in filas if f["id_grupo"] == 10)

        self.assertEqual(fila["codigo_acceso"], "VIGENTE1")
        self.assertIsNotNone(fila["fecha_expiracion_codigo"])
        self.assertGreater(fila["segundos_restantes_codigo"], 0)

    def test_miembro_no_lider_no_ve_codigo_ni_fecha(self):
        filas = grupo_service.listar_grupos_de_usuario(self.db, 2, es_admin=False)
        fila = next(f for f in filas if f["id_grupo"] == 10)

        self.assertIsNone(fila["codigo_acceso"])
        self.assertIsNone(fila["fecha_expiracion_codigo"])
        self.assertIsNone(fila["segundos_restantes_codigo"])

    def test_admin_ve_codigo_en_grupo_donde_no_es_lider(self):
        filas = grupo_service.listar_grupos_de_usuario(self.db, 4, es_admin=True)
        fila = next(f for f in filas if f["id_grupo"] == 10)

        self.assertEqual(fila["codigo_acceso"], "VIGENTE1")
        self.assertIsNotNone(fila["fecha_expiracion_codigo"])
        self.assertGreater(fila["segundos_restantes_codigo"], 0)

    def test_listar_todos_los_grupos_muestra_codigo(self):
        filas = grupo_service.listar_todos_los_grupos(self.db)
        por_id = {f["id_grupo"]: f for f in filas}

        self.assertEqual(por_id[10]["codigo_acceso"], "VIGENTE1")
        self.assertEqual(por_id[11]["codigo_acceso"], "VENCIDO1")
        self.assertEqual(por_id[12]["codigo_acceso"], "SINFECHA")


class SegundosRestantesTests(VigenciaBase):
    def test_vigente_tiene_segundos_positivos(self):
        datos = grupo_service.serializar_grupo(self.db.get(Grupo, 10), incluir_codigo=True)

        self.assertGreater(datos["segundos_restantes_codigo"], 0)
        self.assertLessEqual(datos["segundos_restantes_codigo"], 30 * 60)

    def test_vencido_tiene_cero(self):
        datos = grupo_service.serializar_grupo(self.db.get(Grupo, 11), incluir_codigo=True)

        self.assertEqual(datos["segundos_restantes_codigo"], 0)

    def test_sin_fecha_tiene_cero(self):
        datos = grupo_service.serializar_grupo(self.db.get(Grupo, 12), incluir_codigo=True)

        self.assertEqual(datos["segundos_restantes_codigo"], 0)


if __name__ == "__main__":
    unittest.main()
