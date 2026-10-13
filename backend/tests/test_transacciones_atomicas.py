import unittest
from datetime import datetime
from unittest.mock import patch

import app.models  # noqa: F401
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.asignacion_tarea import AsignacionTarea
from app.models.categoria import Categoria
from app.models.grupo import Grupo
from app.models.historial_tarea import HistorialTarea
from app.models.integrante import Integrante
from app.models.perfil import Perfil
from app.models.tarea import Tarea
from app.models.usuario import Usuario
from app.schemas.tarea import TareaGrupalCreate, TareaUpdate
from app.services import grupo_service, tarea_service


class TransaccionesAtomicasTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

        @event.listens_for(self.engine, "connect")
        def activar_claves_foraneas(conexion, _):
            conexion.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def usuario(self, correo):
        usuario = Usuario(correo_electronico=correo, contrasena="hash-sintetico")
        self.db.add(usuario)
        self.db.flush()
        return usuario

    def categoria(self):
        categoria = Categoria(nombre_categoria="Lectura")
        self.db.add(categoria)
        self.db.flush()
        return categoria

    def test_crear_grupo_revierte_grupo_si_falla_el_lider(self):
        lider = self.usuario("lider@example.test")
        self.db.commit()

        with patch.object(
            grupo_service.grupo_repository,
            "agregar_integrante",
            side_effect=RuntimeError("fallo-sintetico-al-crear-lider"),
        ):
            with self.assertRaisesRegex(RuntimeError, "fallo-sintetico"):
                grupo_service.crear_grupo(self.db, "Grupo", None, lider.id_usuario)

        self.assertEqual(self.db.query(Grupo).count(), 0)
        self.assertEqual(self.db.query(Integrante).count(), 0)

    def test_crear_tarea_grupal_revierte_tarea_y_asignaciones_parciales(self):
        lider = self.usuario("lider@example.test")
        miembro = self.usuario("miembro@example.test")
        categoria = self.categoria()
        grupo = Grupo(nombre_grupo="Grupo", codigo_acceso="ABC12345")
        self.db.add(grupo)
        self.db.flush()
        integrantes = [
            Integrante(id_usuario=lider.id_usuario, id_grupo=grupo.id_grupo, rol="lider"),
            Integrante(id_usuario=miembro.id_usuario, id_grupo=grupo.id_grupo, rol="miembro"),
        ]
        self.db.add_all(integrantes)
        self.db.commit()

        crear_asignacion_real = tarea_service.asignacion_tarea_repository.crear_asignacion
        llamadas = 0

        def fallar_en_segunda_asignacion(db, id_tarea, id_integrante, commit=True):
            nonlocal llamadas
            llamadas += 1
            if llamadas == 2:
                raise RuntimeError("fallo-sintetico-en-asignacion")
            return crear_asignacion_real(db, id_tarea, id_integrante, commit=commit)

        datos = TareaGrupalCreate(
            nombre="Entrega grupal",
            fecha_entrega=datetime(2026, 10, 20, 12),
            dificultad_estimada=3,
            tiempo_estimado=45,
            id_categoria=categoria.id_categoria,
            ids_usuarios=[lider.id_usuario, miembro.id_usuario],
        )
        with patch.object(
            tarea_service.asignacion_tarea_repository,
            "crear_asignacion",
            side_effect=fallar_en_segunda_asignacion,
        ):
            with self.assertRaisesRegex(RuntimeError, "fallo-sintetico"):
                tarea_service.crear_tarea_grupal(
                    self.db,
                    grupo.id_grupo,
                    datos,
                    lider,
                )

        self.assertEqual(self.db.query(Tarea).count(), 0)
        self.assertEqual(self.db.query(AsignacionTarea).count(), 0)

    def test_completar_tarea_revierte_estado_si_falla_el_recalculo(self):
        usuario = self.usuario("estudiante@example.test")
        categoria = self.categoria()
        tarea = Tarea(
            nombre="Lectura",
            fecha_entrega=datetime(2026, 10, 20, 12),
            estado="Pendiente",
            dificultad_estimada=2,
            tiempo_estimado=30,
            tiempo_acumulado=0,
            id_usuario=usuario.id_usuario,
            id_categoria=categoria.id_categoria,
        )
        self.db.add(tarea)
        self.db.commit()
        id_tarea = tarea.id_tarea

        with patch(
            "app.services.estadistica_service.recalcular_estadistica_categoria",
            side_effect=RuntimeError("fallo-sintetico-en-estadisticas"),
        ):
            with self.assertRaisesRegex(RuntimeError, "fallo-sintetico"):
                tarea_service.actualizar_tarea(
                    self.db, id_tarea, TareaUpdate(estado="Completada"), usuario.id_usuario
                )

        self.db.expire_all()
        self.assertEqual(self.db.get(Tarea, id_tarea).estado, "Pendiente")
        self.assertEqual(self.db.query(HistorialTarea).count(), 0)

    def test_reabrir_conserva_historial_y_una_nueva_completacion_crea_otro(self):
        usuario = self.usuario("estudiante@example.test")
        categoria = self.categoria()
        perfil = Perfil(nombre_usuario="Estudiante", id_usuario=usuario.id_usuario)
        tarea = Tarea(
            nombre="Lectura",
            fecha_entrega=datetime(2026, 10, 20, 12),
            estado="Pendiente",
            dificultad_estimada=2,
            tiempo_estimado=30,
            tiempo_acumulado=0,
            id_usuario=usuario.id_usuario,
            id_categoria=categoria.id_categoria,
        )
        self.db.add_all([perfil, tarea])
        self.db.commit()
        id_tarea = tarea.id_tarea

        tarea_service.actualizar_tarea(
            self.db, id_tarea, TareaUpdate(estado="Completada"), usuario.id_usuario
        )
        tarea_service.actualizar_tarea(
            self.db, id_tarea, TareaUpdate(estado="Pendiente"), usuario.id_usuario
        )
        self.assertEqual(self.db.query(HistorialTarea).filter_by(id_tarea=id_tarea).count(), 1)

        tarea_service.actualizar_tarea(
            self.db, id_tarea, TareaUpdate(estado="Completada"), usuario.id_usuario
        )
        self.assertEqual(self.db.query(HistorialTarea).filter_by(id_tarea=id_tarea).count(), 2)


if __name__ == "__main__":
    unittest.main()
