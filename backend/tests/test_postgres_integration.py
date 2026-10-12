"""Pruebas optativas con PostgreSQL en una base cuyo nombre incluye "test".

La suite crea un esquema temporal con nombre aleatorio y solo lo elimina a él.
Para habilitarla, definir ACADEX_RUN_POSTGRES_TESTS=1 y configurar las variables
DB_* para una base aislada como acadex_test.
"""

import io
import os
import tempfile
import unittest
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException, UploadFile
from sqlalchemy import DateTime, Integer, String, create_engine, event, inspect, text
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
from app.config.settings import settings
from app.core.legal import VERSION_AVISO_ALMACENAMIENTO, VERSION_POLITICA_DATOS


_EJECUTAR = os.getenv("ACADEX_RUN_POSTGRES_TESTS") == "1"


@unittest.skipUnless(
    _EJECUTAR,
    "Define ACADEX_RUN_POSTGRES_TESTS=1 para usar la base PostgreSQL aislada.",
)
class PostgreSQLIntegracionTests(unittest.TestCase):
    def setUp(self):
        self.admin_engine = create_engine(settings.database_url)
        with self.admin_engine.connect() as connection:
            database_name = connection.execute(text("SELECT current_database()")).scalar_one()
        if "test" not in database_name.lower():
            self.admin_engine.dispose()
            self.fail(
                "Pruebas bloqueadas: la base indicada no contiene 'test' en su nombre. "
                "Usa una base aislada, por ejemplo acadex_test."
            )

        self.schema_name = f"acadex_test_{uuid.uuid4().hex}"
        with self.admin_engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{self.schema_name}"'))

        self.engine = create_engine(
            settings.database_url,
            connect_args={"options": f"-c search_path={self.schema_name}"},
        )
        try:
            Base.metadata.create_all(self.engine)
        except Exception:
            self.engine.dispose()
            with self.admin_engine.begin() as connection:
                connection.execute(text(f'DROP SCHEMA "{self.schema_name}" CASCADE'))
            self.admin_engine.dispose()
            raise

    def tearDown(self):
        self.engine.dispose()
        with self.admin_engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{self.schema_name}" CASCADE'))
        self.admin_engine.dispose()

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
