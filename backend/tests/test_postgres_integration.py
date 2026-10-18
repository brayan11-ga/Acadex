"""Pruebas optativas que solo se habilitarán desde un runner aislado de Compose.

La configuración test-only y el marcador operativo se validan antes de importar
la aplicación o SQLAlchemy. El Compose actual no proporciona ese marcador, por
lo que esta integración permanece bloqueada hasta implementar el runner aislado.
"""

import io
import os
import sys
import tempfile
import unittest
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app.testing.postgres_safety import (
    TEST_RUNNER_MARKER_PATH,
    UnsafeTestDatabaseError,
    crear_engine_pruebas,
    crear_esquema_pruebas,
    eliminar_esquema_pruebas,
    proyectar_configuracion_pruebas_backend,
    validar_configuracion_pruebas,
    validar_runner_compose_aislado,
)


_EJECUTAR = os.getenv("ACADEX_RUN_POSTGRES_TESTS") == "1"
_TEST_CONFIG = None

if _EJECUTAR:
    _CONFIGURACION_PRECARGADA = {
        "app.config.settings",
        "app.db.session",
        "app.main",
    }.intersection(sys.modules)
    if _CONFIGURACION_PRECARGADA:
        raise UnsafeTestDatabaseError(
            "Ejecuta la integración PostgreSQL en un proceso de pruebas dedicado; "
            "ya se cargaron módulos de configuración o sesión del backend."
        )

    # Estas guardas deben preceder a cualquier import que pueda construir el
    # engine global de app.db.session.
    _TEST_CONFIG = validar_configuracion_pruebas(os.environ)
    _EN_CONTENEDOR = Path("/.dockerenv").is_file()
    _MARCADOR_AISLAMIENTO = Path(TEST_RUNNER_MARKER_PATH).is_file()
    validar_runner_compose_aislado(
        os.environ,
        en_contenedor=_EN_CONTENEDOR,
        marcador_aislamiento_presente=_MARCADOR_AISLAMIENTO,
    )
    proyectar_configuracion_pruebas_backend(_TEST_CONFIG, os.environ)

    from fastapi import HTTPException, UploadFile
    from sqlalchemy import DateTime, Integer, String, create_engine, event, inspect, text
    from sqlalchemy.engine import URL
    from sqlalchemy.orm import Session
    from starlette.datastructures import Headers

    from app.db.base import Base
    import app.models  # noqa: F401 - registra todos los modelos en metadata
    from app.models.archivo import Archivo
    from app.models.asignacion_tarea import AsignacionTarea
    from app.models.categoria import Categoria
    from app.models.consentimiento_usuario import ConsentimientoUsuario
    from app.models.grupo import Grupo
    from app.models.integrante import Integrante
    from app.models.perfil import Perfil
    from app.models.tarea import Tarea
    from app.models.usuario import Usuario
    from app.services import archivo_service, usuario_service
    from app.core.legal import VERSION_AVISO_ALMACENAMIENTO, VERSION_POLITICA_DATOS


def _crear_engine_sqlalchemy(config, **options):
    """Construye la URL solo con credenciales de pruebas ya validadas."""
    return create_engine(
        URL.create(
            "postgresql+psycopg2",
            username=config.username,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
        ),
        **options,
    )


def _crear_engine_postgres_pruebas(**options):
    return crear_engine_pruebas(
        os.environ,
        lambda config: _crear_engine_sqlalchemy(config, **options),
        en_contenedor=Path("/.dockerenv").is_file(),
        marcador_aislamiento_presente=Path(TEST_RUNNER_MARKER_PATH).is_file(),
    )


@unittest.skipUnless(
    _EJECUTAR,
    "Define ACADEX_RUN_POSTGRES_TESTS=1 para usar la base PostgreSQL aislada.",
)
class PostgreSQLIntegracionTests(unittest.TestCase):
    def setUp(self):
        self.admin_engine = _crear_engine_postgres_pruebas()
        self.schema_name = f"acadex_test_{uuid.uuid4().hex}"
        try:
            crear_esquema_pruebas(
                self.admin_engine,
                self.schema_name,
                configured_database=_TEST_CONFIG.database,
                expected_database=_TEST_CONFIG.database,
                run_postgres_tests=os.getenv("ACADEX_RUN_POSTGRES_TESTS"),
            )
        except Exception:
            self.admin_engine.dispose()
            raise

        self.engine = _crear_engine_postgres_pruebas(
            connect_args={"options": f"-c search_path={self.schema_name}"},
        )
        try:
            Base.metadata.create_all(self.engine)
        except Exception:
            self.engine.dispose()
            eliminar_esquema_pruebas(
                self.admin_engine,
                self.schema_name,
                configured_database=_TEST_CONFIG.database,
                expected_database=_TEST_CONFIG.database,
                run_postgres_tests=os.getenv("ACADEX_RUN_POSTGRES_TESTS"),
            )
            self.admin_engine.dispose()
            raise

    def tearDown(self):
        self.engine.dispose()
        eliminar_esquema_pruebas(
            self.admin_engine,
            self.schema_name,
            configured_database=_TEST_CONFIG.database,
            expected_database=_TEST_CONFIG.database,
            run_postgres_tests=os.getenv("ACADEX_RUN_POSTGRES_TESTS"),
        )
        self.admin_engine.dispose()

    def test_historia_alembic_y_esquema_publico_coinciden_con_modelos(self):
        inspector = inspect(self.admin_engine)
        tablas_modelo = set(Base.metadata.tables)
        tablas_publicas = set(inspector.get_table_names(schema="public"))

        self.assertEqual(len(tablas_modelo), 18)
        self.assertEqual(tablas_publicas - {"alembic_version"}, tablas_modelo)
        with self.admin_engine.connect() as connection:
            revisiones = connection.execute(
                text("SELECT version_num FROM public.alembic_version")
            ).scalars().all()
            categorias_iniciales = connection.execute(
                text("SELECT count(*) FROM public.categorias")
            ).scalar_one()
        self.assertEqual(revisiones, ["20261016_06"])
        self.assertEqual(categorias_iniciales, 9)

        dialect = self.admin_engine.dialect
        for table_name, expected_table in Base.metadata.tables.items():
            with self.subTest(table=table_name):
                actual_columns = {
                    column["name"]: column
                    for column in inspector.get_columns(table_name, schema="public")
                }
                self.assertEqual(set(actual_columns), set(expected_table.columns.keys()))

                for expected_column in expected_table.columns:
                    actual_column = actual_columns[expected_column.name]
                    self.assertEqual(actual_column["nullable"], expected_column.nullable)
                    self.assertEqual(
                        actual_column["type"].compile(dialect=dialect).upper(),
                        expected_column.type.compile(dialect=dialect).upper(),
                    )
                    self.assertEqual(
                        actual_column.get("identity") is not None,
                        expected_column.identity is not None,
                    )
                    if expected_column.identity is not None:
                        self.assertEqual(
                            actual_column["identity"].get("always"),
                            expected_column.identity.always,
                        )
                    self.assertEqual(
                        actual_column.get("default") is not None,
                        expected_column.server_default is not None
                        and expected_column.identity is None,
                    )

                expected_index_names = {index.name for index in expected_table.indexes}
                actual_indexes = {
                    index["name"]: index
                    for index in inspector.get_indexes(table_name, schema="public")
                }
                self.assertTrue(expected_index_names.issubset(actual_indexes))
                for expected_index in expected_table.indexes:
                    actual_index = actual_indexes[expected_index.name]
                    self.assertEqual(
                        actual_index["column_names"],
                        [column.name for column in expected_index.columns],
                    )
                    self.assertEqual(actual_index["unique"], expected_index.unique)

    def test_esquema_publico_inicializado_coincide_con_modelos_y_migraciones(self):
        inspector = inspect(self.admin_engine)
        consentimientos = inspector.get_columns("consentimientos_usuario", schema="public")
        self.assertEqual(
            {columna["name"] for columna in consentimientos},
            {
                "id_consentimiento", "id_usuario", "tipo_consentimiento",
                "version_politica", "fecha_aceptacion",
            },
        )
        consentimientos_por_nombre = {columna["name"]: columna for columna in consentimientos}
        self.assertEqual(consentimientos_por_nombre["id_usuario"]["nullable"], False)
        self.assertEqual(consentimientos_por_nombre["tipo_consentimiento"]["type"].length, 40)
        self.assertEqual(consentimientos_por_nombre["version_politica"]["type"].length, 30)
        self.assertIsInstance(consentimientos_por_nombre["tipo_consentimiento"]["type"], String)
        self.assertIsInstance(consentimientos_por_nombre["fecha_aceptacion"]["type"], DateTime)
        self.assertTrue(consentimientos_por_nombre["fecha_aceptacion"]["type"].timezone)
        uploader = next(
            columna for columna in inspector.get_columns("archivos", schema="public")
            if columna["name"] == "id_usuario_subida"
        )
        self.assertTrue(uploader["nullable"])
        self.assertIsInstance(uploader["type"], Integer)
        identidad = next(
            columna for columna in consentimientos
            if columna["name"] == "id_consentimiento"
        )
        self.assertIsNotNone(identidad.get("identity"))
        self.assertFalse(identidad["identity"]["always"])
        consentimientos_fk = inspector.get_foreign_keys(
            "consentimientos_usuario", schema="public"
        )
        self.assertTrue(
            any(
                fk["constrained_columns"] == ["id_usuario"]
                and fk["referred_table"] == "usuarios"
                and fk["options"].get("ondelete") == "CASCADE"
                for fk in consentimientos_fk
            )
        )
        self.assertIsNotNone(ConsentimientoUsuario.__table__.c.id_consentimiento.identity)
        archivos_fk = inspector.get_foreign_keys("archivos", schema="public")
        self.assertTrue(
            any(
                fk["constrained_columns"] == ["id_usuario_subida"]
                and fk["referred_table"] == "usuarios"
                and fk["options"].get("ondelete") == "SET NULL"
                for fk in archivos_fk
            )
        )
        self.assertIn(
            "uq_consentimientos_usuario_version",
            {
                constraint["name"]
                for constraint in inspector.get_unique_constraints(
                    "consentimientos_usuario", schema="public"
                )
            },
        )
        self.assertIn(
            "chk_consentimientos_usuario_tipo",
            {
                constraint["name"]
                for constraint in inspector.get_check_constraints(
                    "consentimientos_usuario", schema="public"
                )
            },
        )

    def test_registro_guarda_perfil_y_las_dos_evidencias_en_postgresql(self):
        correo = f"registro-{uuid.uuid4().hex}@example.test"
        with Session(self.engine) as db:
            usuario = usuario_service.registrar_usuario(
                db,
                correo,
                "ClaveSegura123",
                True,
                True,
                nombre_usuario="Nombre PostgreSQL",
            )
            perfil = db.query(Perfil).filter_by(id_usuario=usuario.id_usuario).one()
            evidencias = db.query(ConsentimientoUsuario).filter_by(
                id_usuario=usuario.id_usuario
            ).all()

            self.assertEqual(perfil.nombre_usuario, "Nombre PostgreSQL")
            self.assertEqual(
                {evidencia.tipo_consentimiento for evidencia in evidencias},
                {"tratamiento_datos", "aviso_almacenamiento"},
            )
            self.assertEqual(
                {evidencia.version_politica for evidencia in evidencias},
                {VERSION_POLITICA_DATOS, VERSION_AVISO_ALMACENAMIENTO},
            )
            self.assertEqual(len(evidencias), 2)

    def test_fallo_al_confirmar_registro_no_deja_usuario_perfil_ni_evidencias(self):
        correo = f"rollback-{uuid.uuid4().hex}@example.test"
        with Session(self.engine) as db:
            def abortar_commit(_session):
                raise RuntimeError("fallo de persistencia de prueba")

            event.listen(db, "before_commit", abortar_commit, once=True)
            try:
                with self.assertRaisesRegex(RuntimeError, "fallo de persistencia"):
                    usuario_service.registrar_usuario(
                        db,
                        correo,
                        "ClaveSegura123",
                        True,
                        True,
                        nombre_usuario="Nombre rollback",
                    )
            finally:
                if event.contains(db, "before_commit", abortar_commit):
                    event.remove(db, "before_commit", abortar_commit)

        with Session(self.engine) as verificacion:
            usuario = verificacion.query(Usuario).filter_by(correo_electronico=correo).first()
            self.assertIsNone(usuario)
            self.assertEqual(verificacion.query(Perfil).count(), 0)
            self.assertEqual(verificacion.query(ConsentimientoUsuario).count(), 0)

    def test_archivos_grupales_respetan_autoria_listado_descarga_y_borrado(self):
        with Session(self.engine) as db:
            usuario_a = Usuario(correo_electronico="autor@example.test", contrasena="hash")
            usuario_b = Usuario(correo_electronico="integrante@example.test", contrasena="hash")
            usuario_c = Usuario(correo_electronico="autor-historico@example.test", contrasena="hash")
            categoria = Categoria(nombre_categoria="Integración")
            grupo = Grupo(nombre_grupo="Grupo de prueba", codigo_acceso=uuid.uuid4().hex[:20])
            db.add_all([usuario_a, usuario_b, usuario_c, categoria, grupo])
            db.flush()

            integrante_a = Integrante(rol="miembro", id_usuario=usuario_a.id_usuario, id_grupo=grupo.id_grupo)
            integrante_b = Integrante(rol="miembro", id_usuario=usuario_b.id_usuario, id_grupo=grupo.id_grupo)
            db.add_all([integrante_a, integrante_b])
            db.flush()
            tarea = Tarea(
                nombre="Tarea de integración",
                fecha_entrega=datetime(2030, 1, 1),
                estado="pendiente",
                dificultad_estimada=2,
                tiempo_estimado=30,
                id_grupo=grupo.id_grupo,
                id_categoria=categoria.id_categoria,
            )
            db.add(tarea)
            db.flush()
            db.add_all([
                AsignacionTarea(id_tarea=tarea.id_tarea, id_integrante=integrante_a.id_integrante),
                AsignacionTarea(id_tarea=tarea.id_tarea, id_integrante=integrante_b.id_integrante),
                Archivo(
                    nombre="historico.pdf", tamano=10, tipo="PDF",
                    ruta=f"{tarea.id_tarea}/historico.pdf", id_tarea=tarea.id_tarea,
                    id_usuario_subida=None,
                ),
                Archivo(
                    nombre="autor-eliminado.pdf", tamano=10, tipo="PDF",
                    ruta=f"{tarea.id_tarea}/autor-eliminado.pdf", id_tarea=tarea.id_tarea,
                    id_usuario_subida=usuario_c.id_usuario,
                ),
            ])
            db.commit()
            archivo_autor_eliminado = db.query(Archivo).filter_by(
                nombre="autor-eliminado.pdf"
            ).one()
            db.delete(usuario_c)
            db.commit()
            db.refresh(archivo_autor_eliminado)
            self.assertIsNone(archivo_autor_eliminado.id_usuario_subida)

            with tempfile.TemporaryDirectory() as directorio:
                with patch.object(archivo_service, "DIRECTORIO_BASE_UPLOADS", Path(directorio)):
                    subida = archivo_service.subir_archivo_tarea(
                        db,
                        tarea.id_tarea,
                        UploadFile(
                            file=io.BytesIO(b"%PDF-1.7\nprueba"),
                            filename="entrega.pdf",
                            headers=Headers({"content-type": "application/pdf"}),
                        ),
                        usuario_a.id_usuario,
                    )
                    archivos = archivo_service.listar_archivos_de_tarea(
                        db, tarea.id_tarea, usuario_b.id_usuario
                    )
                    listado_subido = next(
                        item for item in archivos if item["id_archivo"] == subida["id_archivo"]
                    )
                    listado_historico = next(item for item in archivos if item["nombre"] == "historico.pdf")
                    self.assertFalse(listado_subido["puede_eliminar"])
                    self.assertFalse(listado_historico["puede_eliminar"])

                    registro, ruta = archivo_service.obtener_archivo_para_descarga(
                        db, tarea.id_tarea, subida["id_archivo"], usuario_b.id_usuario
                    )
                    self.assertEqual(registro.id_usuario_subida, usuario_a.id_usuario)
                    self.assertTrue(ruta.is_file())

                    with self.assertRaises(HTTPException) as no_autorizado:
                        archivo_service.eliminar_archivo_tarea(
                            db, tarea.id_tarea, subida["id_archivo"], usuario_b.id_usuario
                        )
                    self.assertEqual(no_autorizado.exception.status_code, 403)

                    archivo_service.eliminar_archivo_tarea(
                        db, tarea.id_tarea, subida["id_archivo"], usuario_a.id_usuario
                    )
                    self.assertIsNone(
                        db.query(Archivo).filter_by(id_archivo=subida["id_archivo"]).first()
                    )


if __name__ == "__main__":
    unittest.main()
