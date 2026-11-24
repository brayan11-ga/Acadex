# Ruta: backend/tests/test_c4a_correcciones_previas.py
# Pruebas de la Fase C4a. SIN VERIFICAR: no se ejecutaron en esta sesión.
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

import app.models  # noqa: F401
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models.categoria import Categoria
from app.models.estadistica_categoria import EstadisticaCategoria
from app.models.grupo import Grupo
from app.models.historial_tarea import HistorialTarea
from app.models.perfil import Perfil
from app.models.tarea import Tarea
from app.models.usuario import Usuario
from app.repositories.estadisticas_repository import estadisticas_repository
from app.schemas.tarea import TareaCreate, TareaGrupalCreate, TareaUpdate
from app.services import estadistica_service, tarea_service


class EstadisticasSinGrupalesTests(unittest.TestCase):
    """Las estadísticas personales solo cuentan historial con id_grupo NULL."""

    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

        @event.listens_for(self.engine, "connect")
        def activar_claves_foraneas(conexion, _):
            conexion.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        self.usuario = Usuario(
            correo_electronico="estudiante@example.test", contrasena="hash-sintetico"
        )
        self.db.add(self.usuario)
        self.db.flush()
        self.perfil = Perfil(
            nombre_usuario="Estudiante", id_usuario=self.usuario.id_usuario
        )
        self.categoria = Categoria(nombre_categoria="Lectura")
        self.grupo = Grupo(nombre_grupo="Grupo", codigo_acceso="ABC12345")
        self.db.add_all([self.perfil, self.categoria, self.grupo])
        self.db.flush()

        self.tarea_individual = Tarea(
            nombre="Individual",
            fecha_entrega=datetime(2026, 10, 20, 12),
            dificultad_estimada=2,
            tiempo_estimado=30,
            id_usuario=self.usuario.id_usuario,
            id_categoria=self.categoria.id_categoria,
        )
        self.tarea_grupal = Tarea(
            nombre="Grupal",
            fecha_entrega=datetime(2026, 10, 20, 12),
            dificultad_estimada=4,
            tiempo_estimado=60,
            id_grupo=self.grupo.id_grupo,
            id_categoria=self.categoria.id_categoria,
        )
        self.db.add_all([self.tarea_individual, self.tarea_grupal])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _historial(self, tarea, id_grupo, dificultad, tiempo):
        fila = HistorialTarea(
            fechahora_fin=datetime.now(),
            tiempo_real=tiempo,
            dificultad_real=dificultad,
            id_usuario=self.usuario.id_usuario,
            id_tarea=tarea.id_tarea,
            id_grupo=id_grupo,
        )
        self.db.add(fila)
        self.db.commit()
        return fila

    def test_recalcular_cuenta_solo_historial_individual(self):
        self._historial(self.tarea_individual, None, 3, 100)
        self._historial(self.tarea_grupal, self.grupo.id_grupo, 5, 200)

        estadistica_service.recalcular_estadistica_categoria(
            self.db, self.usuario.id_usuario, self.categoria.id_categoria
        )

        estadistica = (
            self.db.query(EstadisticaCategoria)
            .filter(
                EstadisticaCategoria.id_perfil == self.perfil.id_perfil,
                EstadisticaCategoria.id_categoria == self.categoria.id_categoria,
            )
            .one()
        )
        self.assertEqual(estadistica.total_tareas, 1)
        self.assertEqual(estadistica.promedio_dificultad, 3)
        self.assertEqual(estadistica.promedio_tiempo, 100)

    def test_recalcular_borra_estadistica_si_solo_hay_grupales(self):
        estadistica = EstadisticaCategoria(
            id_perfil=self.perfil.id_perfil,
            id_categoria=self.categoria.id_categoria,
            promedio_tiempo=200,
            promedio_dificultad=5,
            total_tareas=1,
        )
        self.db.add(estadistica)
        self.db.commit()
        self._historial(self.tarea_grupal, self.grupo.id_grupo, 5, 200)

        estadistica_service.recalcular_estadistica_categoria(
            self.db, self.usuario.id_usuario, self.categoria.id_categoria
        )

        self.assertIsNone(
            self.db.query(EstadisticaCategoria)
            .filter(
                EstadisticaCategoria.id_perfil == self.perfil.id_perfil,
                EstadisticaCategoria.id_categoria == self.categoria.id_categoria,
            )
            .first()
        )

    def test_resumen_semanal_excluye_historial_grupal(self):
        self._historial(self.tarea_individual, None, 3, 100)
        self._historial(self.tarea_grupal, self.grupo.id_grupo, 5, 200)
        ahora = datetime.now()

        filas = estadisticas_repository.obtener_historial_rango(
            self.db,
            self.usuario.id_usuario,
            ahora - timedelta(days=1),
            ahora + timedelta(days=1),
        )

        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0][0].id_tarea, self.tarea_individual.id_tarea)


class ValidacionDificultadYTiempoTests(unittest.TestCase):
    """Dificultad 1..5 y tiempo > 0 se validan en el schema (422, no 500)."""

    def _datos_base(self):
        return {
            "nombre": "Tarea",
            "fecha_entrega": datetime(2026, 10, 20, 12),
            "id_categoria": 1,
        }

    def test_tarea_create_rechaza_dificultad_fuera_de_rango(self):
        for dificultad in (0, 6, 30):
            with self.subTest(dificultad=dificultad):
                with self.assertRaises(ValidationError):
                    TareaCreate(
                        **self._datos_base(),
                        dificultad_estimada=dificultad,
                        tiempo_estimado=30,
                    )

    def test_tarea_create_rechaza_tiempo_no_positivo(self):
        for tiempo in (0, -5):
            with self.subTest(tiempo=tiempo):
                with self.assertRaises(ValidationError):
                    TareaCreate(
                        **self._datos_base(),
                        dificultad_estimada=3,
                        tiempo_estimado=tiempo,
                    )

    def test_tarea_grupal_create_rechaza_valores_invalidos(self):
        with self.assertRaises(ValidationError):
            TareaGrupalCreate(
                **self._datos_base(), dificultad_estimada=30, tiempo_estimado=30
            )
        with self.assertRaises(ValidationError):
            TareaGrupalCreate(
                **self._datos_base(), dificultad_estimada=3, tiempo_estimado=0
            )

    def test_tarea_update_rechaza_valores_invalidos(self):
        with self.assertRaises(ValidationError):
            TareaUpdate(dificultad_estimada=6)
        with self.assertRaises(ValidationError):
            TareaUpdate(tiempo_estimado=0)

    def test_valores_validos_pasan(self):
        self.assertEqual(
            TareaCreate(
                **self._datos_base(), dificultad_estimada=5, tiempo_estimado=1
            ).dificultad_estimada,
            5,
        )
        self.assertEqual(TareaUpdate(dificultad_estimada=1).dificultad_estimada, 1)
        self.assertEqual(TareaUpdate(tiempo_estimado=1).tiempo_estimado, 1)


class CrearTareaGrupalAsignadosTests(unittest.TestCase):
    """Lista vacía o con repetidos se rechaza antes de tocar la BD."""

    def _datos(self, ids_usuarios):
        return TareaGrupalCreate(
            nombre="Tarea",
            fecha_entrega=datetime(2026, 10, 20, 12),
            dificultad_estimada=3,
            tiempo_estimado=30,
            id_categoria=1,
            ids_usuarios=ids_usuarios,
        )

    def _crear(self, ids_usuarios):
        actor = SimpleNamespace(id_usuario=12, es_admin=False)
        with patch.object(tarea_service, "_es_lider", return_value=True):
            with self.assertRaises(HTTPException) as error:
                tarea_service.crear_tarea_grupal(
                    Mock(), 7, self._datos(ids_usuarios), actor
                )
        return error.exception

    def test_lista_vacia_devuelve_400(self):
        error = self._crear([])
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.detail, "La tarea debe tener al menos un asignado.")

    def test_ids_repetidos_devuelven_400(self):
        error = self._crear([13, 13])
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.detail, "No se permiten asignados repetidos.")


if __name__ == "__main__":
    unittest.main()
