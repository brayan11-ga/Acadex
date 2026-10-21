# Ruta: backend/tests/test_api_autorizacion.py
import sys
import unittest
from datetime import date, datetime, timedelta
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from fastapi.dependencies import utils as fastapi_dependency_utils
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as SQLSession
from starlette.requests import Request

# These integrations are not needed by authorization tests and may be absent
# from a minimal test environment. No AI or PDF analysis is exercised here.
sys.modules.setdefault("pdfplumber", ModuleType("pdfplumber"))
try:
    from google import genai as _google_genai  # noqa: F401
    from google.genai import types as _google_genai_types  # noqa: F401
except ImportError:
    google_module = sys.modules.setdefault("google", ModuleType("google"))
    if not hasattr(google_module, "__path__"):
        google_module.__path__ = []
    genai_module = ModuleType("google.genai")
    genai_module.Client = lambda **_kwargs: None
    types_module = ModuleType("google.genai.types")
    types_module.GenerateContentConfig = lambda **kwargs: kwargs
    genai_module.types = types_module
    sys.modules["google.genai"] = genai_module
    sys.modules["google.genai.types"] = types_module
    google_module.genai = genai_module

# The task router declares upload fields, but these tests do not exercise file
# uploads. The current test runtime omits python-multipart, so skip only the
# framework's import-time guard while registering the unrelated API routes.
fastapi_dependency_utils.ensure_multipart_is_installed = lambda: None

from app.core.security import create_access_token
from app.dependencies.auth import get_usuario_actual, security_scheme
from app.main import api, health_live, health_ready
from app.db.base import Base
from app.db.session import engine
from app.models.categoria import Categoria
from app.models.grupo import Grupo
from app.models.integrante import Integrante
from app.models.tarea import Tarea
from app.api.v1.endpoints.sesiones_cronometro import iniciar_sesion as iniciar_sesion_endpoint
from app.models.usuario import Usuario
from app.repositories import tarea_repository
from app.services import perfil_service, sesion_cronometro_service, tarea_service


class QueryUsuarioFalsa:
    def __init__(self):
        self.id_usuario = None

    def filter(self, condicion):
        self.id_usuario = condicion.right.value
        return self

    def first(self):
        return Usuario(
            id_usuario=self.id_usuario,
            correo_electronico="prueba@example.test",
            contrasena="hash-sintetico",
            es_admin=False,
        )


class SesionFalsa:
    def query(self, modelo):
        if modelo is not Usuario:
            raise AssertionError("La prueba no debe consultar otra entidad")
        return QueryUsuarioFalsa()


class AutenticacionRutasTests(unittest.TestCase):
    def test_health_live_no_depende_de_postgresql(self):
        self.assertEqual(health_live(), {"status": "ok"})

    def test_health_ready_consulta_postgresql_y_devuelve_error_seguro(self):
        conexion = Mock()
        with patch.object(engine, "connect") as conectar:
            conectar.return_value.__enter__.return_value = conexion
            self.assertEqual(health_ready(), {"status": "ok"})
        conexion.execute.assert_called_once()
        consulta = conexion.execute.call_args.args[0].text
        self.assertIn("public.limites_solicitud", consulta)
        self.assertIn("public.uso_analisis_ia", consulta)
        self.assertIn("public.bloqueo_cuota_gemini", consulta)

        with (
            patch.object(engine, "connect", side_effect=SQLAlchemyError("fallo-sintetico")),
            self.assertLogs("app.main", level="WARNING"),
        ):
            with self.assertRaises(HTTPException) as error:
                health_ready()
        self.assertEqual(error.exception.status_code, 503)
        self.assertEqual(error.exception.detail, "Base de datos no disponible")

    def test_dependencia_bearer_rechaza_credenciales_ausentes(self):
        solicitud = Request(
            {"type": "http", "method": "GET", "path": "/", "headers": []}
        )
        with self.assertRaises(HTTPException) as error:
            security_scheme(solicitud).send(None)
        self.assertIn(error.exception.status_code, (401, 403))

    def test_todas_las_rutas_privadas_declaran_dependencia_jwt(self):
        rutas_privadas = {
            ("/api/v1/tareas/", "GET"),
            ("/api/v1/tareas/", "POST"),
            ("/api/v1/tareas/analizar-documento", "POST"),
            ("/api/v1/tareas/calendario", "GET"),
            ("/api/v1/tareas/asignadas/mias", "GET"),
            ("/api/v1/tareas/grupos/{id_grupo}", "POST"),
            ("/api/v1/tareas/{id_tarea}", "GET"),
            ("/api/v1/tareas/{id_tarea}", "PUT"),
            ("/api/v1/tareas/{id_tarea}", "DELETE"),
            ("/api/v1/tareas/{id_tarea}/completar", "POST"),
            ("/api/v1/tareas/{id_tarea}/asignados", "GET"),
            ("/api/v1/tareas/grupos/{id_grupo}", "GET"),
            ("/api/v1/perfiles/", "POST"),
            ("/api/v1/perfiles/usuario/{id_usuario}", "GET"),
            ("/api/v1/perfiles/usuario/{id_usuario}", "PATCH"),
            ("/api/v1/sesiones-cronometro/iniciar", "POST"),
            ("/api/v1/sesiones-cronometro/{id_sesion}/finalizar", "PATCH"),
            ("/api/v1/sesiones-cronometro/usuario/{id_usuario}", "GET"),
        }
        for ruta, metodo in rutas_privadas:
            with self.subTest(ruta=ruta, metodo=metodo):
                coincidencias = [
                    registro
                    for registro in api.routes
                    if getattr(registro, "path", None) == ruta
                    and metodo in getattr(registro, "methods", set())
                ]
                self.assertEqual(len(coincidencias), 1)
                self.assertIn(
                    get_usuario_actual,
                    {dependencia.call for dependencia in coincidencias[0].dependant.dependencies},
                )

    def test_jwt_valido_identifica_al_usuario_y_token_invalido_se_rechaza(self):
        credencial = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=create_access_token("37")
        )
        usuario = get_usuario_actual(credencial, SesionFalsa())
        self.assertEqual(usuario.id_usuario, 37)

        token_invalido = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="token-invalido"
        )
        with self.assertRaises(HTTPException) as error:
            get_usuario_actual(token_invalido, SesionFalsa())
        self.assertEqual(error.exception.status_code, 401)

    def test_inicio_de_sesion_rechaza_un_id_usuario_distinto_del_jwt(self):
        actor = SimpleNamespace(id_usuario=12)
        with patch.object(sesion_cronometro_service, "iniciar_sesion") as iniciar:
            with self.assertRaises(HTTPException) as error:
                iniciar_sesion_endpoint(13, 4, None, actor)
        self.assertEqual(error.exception.status_code, 403)
        iniciar.assert_not_called()


class AutorizacionServiciosTests(unittest.TestCase):
    def test_tarea_personal_solo_se_lee_por_su_propietario(self):
        tarea = SimpleNamespace(id_usuario=12, id_grupo=None)
        with patch.object(tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea):
            self.assertIs(tarea_service.obtener_tarea(None, 4, 12), tarea)
            with self.assertRaises(HTTPException) as error:
                tarea_service.obtener_tarea(None, 4, 13)
        self.assertEqual(error.exception.status_code, 403)
        self.assertNotIn("12", error.exception.detail)

    def test_propietario_puede_actualizar_su_tarea_personal(self):
        tarea = SimpleNamespace(
            id_usuario=12,
            id_grupo=None,
            estado="Pendiente",
        )
        with (
            patch.object(tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea),
            patch.object(tarea_service.tarea_repository, "actualizar_tarea", return_value=tarea) as actualizar,
        ):
            self.assertIs(
                tarea_service.actualizar_tarea(
                    None, 4, tarea_service.TareaUpdate(nombre="Propia"), 12
                ),
                tarea,
            )
        actualizar.assert_called_once()

    def test_integrante_puede_leer_tarea_grupal_y_usuario_ajeno_no(self):
        tarea = SimpleNamespace(id_usuario=None, id_grupo=7)
        with (
            patch.object(tarea_service.tarea_repository, "obtener_tarea_por_id", return_value=tarea),
            patch.object(tarea_service.grupo_repository, "obtener_integrante", side_effect=[SimpleNamespace(rol="miembro"), None]),
        ):
            self.assertIs(tarea_service.obtener_tarea(None, 4, 12), tarea)
            with self.assertRaises(HTTPException) as error:
                tarea_service.obtener_tarea(None, 4, 13)
        self.assertEqual(error.exception.status_code, 403)

    def test_listado_de_grupo_exige_pertenencia(self):
        tarea = SimpleNamespace(id_tarea=4, id_grupo=7)
        with (
            patch.object(tarea_service.grupo_repository, "obtener_integrante", side_effect=[SimpleNamespace(rol="miembro"), None]),
            patch.object(tarea_service.tarea_repository, "obtener_tareas_por_grupo", return_value=[tarea]) as listar,
        ):
            self.assertEqual(tarea_service.listar_tareas_de_grupo(None, 7, 12), [tarea])
            with self.assertRaises(HTTPException) as error:
                tarea_service.listar_tareas_de_grupo(None, 7, 13)
        self.assertEqual(error.exception.status_code, 403)
        listar.assert_called_once_with(None, 7)

    def test_calendario_no_acepta_id_de_otro_usuario(self):
        with patch.object(tarea_service.tarea_repository, "obtener_tareas_por_rango") as consultar:
            with self.assertRaises(HTTPException) as error:
                tarea_service.listar_tareas_calendario(
                    None, date(2026, 10, 1), date(2026, 10, 31), 12, 13
                )
        self.assertEqual(error.exception.status_code, 403)
        consultar.assert_not_called()

    def test_creacion_personal_reemplaza_id_usuario_del_cliente(self):
        datos = tarea_service.TareaCreate(
            nombre="Tarea privada",
            fecha_entrega="2026-10-20T12:00:00",
            dificultad_estimada=2,
            tiempo_estimado=30,
            id_categoria=1,
            id_usuario=13,
        )
        actor = SimpleNamespace(id_usuario=12, es_admin=False)
        creada = SimpleNamespace(id_usuario=12)
        with patch.object(tarea_service.tarea_repository, "crear_tarea", return_value=creada) as crear:
            self.assertIs(tarea_service.crear_tarea(None, datos, actor), creada)
        self.assertEqual(crear.call_args.args[1].id_usuario, 12)

    def test_usuario_no_lider_no_crea_tarea_en_grupo_por_ruta_general(self):
        datos = tarea_service.TareaCreate(
            nombre="Tarea de grupo",
            fecha_entrega="2026-10-20T12:00:00",
            dificultad_estimada=2,
            tiempo_estimado=30,
            id_categoria=1,
            id_grupo=7,
        )
        actor = SimpleNamespace(id_usuario=12, es_admin=False)
        with (
            patch.object(tarea_service, "_es_lider", return_value=False),
            patch.object(tarea_service.tarea_repository, "crear_tarea") as crear,
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.crear_tarea(None, datos, actor)
        self.assertEqual(error.exception.status_code, 403)
        crear.assert_not_called()

    def test_lider_y_asignado_pueden_ver_lista_de_asignados(self):
        tarea = SimpleNamespace(id_tarea=4, id_usuario=None, id_grupo=7)
        usuarios = [SimpleNamespace(id_usuario=12, correo_electronico="a@a.com")]
        esperado = [{"id_usuario": 12, "correo_electronico": "a@a.com", "completado": True}]
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service.asignacion_tarea_repository, "obtener_usuarios_asignados", return_value=usuarios) as listar,
            patch.object(tarea_service.historial_tarea_repository, "obtener_usuarios_completados", return_value={12}),
        ):
            self.assertEqual(tarea_service.listar_asignados_de_tarea(None, 4, 12), esperado)
            self.assertEqual(tarea_service.listar_asignados_de_tarea(None, 4, 13), esperado)
        self.assertEqual(listar.call_count, 2)

    def test_integrante_asignado_no_puede_modificar_tarea_grupal(self):
        # C3: en las grupales el PUT queda reservado al líder; el estado solo
        # se mueve con POST /tareas/{id}/completar.
        tarea = SimpleNamespace(
            id_tarea=4,
            id_usuario=None,
            id_grupo=7,
            estado="Pendiente",
            tiempo_acumulado=0,
            dificultad_estimada=2,
            id_categoria=3,
        )
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service, "_es_lider", return_value=False),
            patch.object(tarea_service.tarea_repository, "actualizar_tarea") as actualizar,
        ):
            for datos in (
                tarea_service.TareaUpdate(estado="Pendiente"),
                tarea_service.TareaUpdate(nombre="Ajeno"),
            ):
                with self.assertRaises(HTTPException) as error:
                    tarea_service.actualizar_tarea(None, 4, datos, 12)
                self.assertEqual(error.exception.status_code, 403)
        actualizar.assert_not_called()

    def test_put_no_puede_completar_tarea_grupal(self):
        # C3: completar una tarea grupal ahora se hace con POST /completar.
        tarea = SimpleNamespace(
            id_tarea=4,
            id_usuario=None,
            id_grupo=7,
            estado="Pendiente",
            tiempo_acumulado=120,
            dificultad_estimada=3,
            id_categoria=2,
        )
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(tarea_service.tarea_repository, "actualizar_tarea") as actualizar,
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.actualizar_tarea(
                    Mock(), 4, tarea_service.TareaUpdate(estado="Completada"), 12
                )
        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "Usa Completar mi parte.")
        actualizar.assert_not_called()

    def test_integrante_no_asignado_puede_ver_lista_de_asignados(self):
        # RF-045: cualquier miembro del grupo (aunque no esté asignado) puede ver la lista.
        tarea = SimpleNamespace(id_tarea=4, id_usuario=None, id_grupo=7)
        usuarios = [SimpleNamespace(id_usuario=12, correo_electronico="a@a.com")]
        with (
            patch.object(tarea_service, "obtener_tarea", return_value=tarea),
            patch.object(tarea_service.asignacion_tarea_repository, "obtener_usuarios_asignados", return_value=usuarios) as listar,
            patch.object(tarea_service.historial_tarea_repository, "obtener_usuarios_completados", return_value=set()),
        ):
            self.assertEqual(
                tarea_service.listar_asignados_de_tarea(None, 4, 12),
                [{"id_usuario": 12, "correo_electronico": "a@a.com", "completado": False}],
            )
        listar.assert_called_once()

    def test_usuario_fuera_del_grupo_no_ve_lista_de_asignados(self):
        # Un usuario que no pertenece al grupo (o no es dueño de la individual) no llega:
        # obtener_tarea lanza 403 y no se consulta la lista.
        with (
            patch.object(
                tarea_service,
                "obtener_tarea",
                side_effect=HTTPException(status_code=403, detail="No tienes permiso para acceder a esta tarea."),
            ),
            patch.object(tarea_service.asignacion_tarea_repository, "obtener_usuarios_asignados") as listar,
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.listar_asignados_de_tarea(None, 4, 99)
        self.assertEqual(error.exception.status_code, 403)
        listar.assert_not_called()

    def test_creacion_grupal_valida_lider_y_asignados_antes_de_guardar(self):
        usuario = SimpleNamespace(id_usuario=12, es_admin=False)
        datos = tarea_service.TareaGrupalCreate(
            nombre="Tarea sintética",
            fecha_entrega="2026-10-20T12:00:00",
            dificultad_estimada=3,
            tiempo_estimado=30,
            id_categoria=1,
            ids_usuarios=[13],
        )
        with (
            patch.object(tarea_service, "_es_lider", return_value=True),
            patch.object(tarea_service.grupo_repository, "obtener_integrante", return_value=None),
            patch.object(tarea_service.tarea_repository, "crear_tarea") as crear,
        ):
            with self.assertRaises(HTTPException) as error:
                tarea_service.crear_tarea_grupal(None, 7, datos, usuario)
        self.assertEqual(error.exception.status_code, 400)
        crear.assert_not_called()


class AutorizacionPerfilYSesionTests(unittest.TestCase):
    def test_perfil_no_se_crea_ni_actualiza_a_nombre_de_otro(self):
        with (
            patch.object(perfil_service.repo, "create_perfil") as crear,
            patch.object(perfil_service.repo, "get_perfil_by_usuario") as obtener,
        ):
            with self.assertRaises(HTTPException) as crear_error:
                perfil_service.crear_perfil(None, {"id_usuario": 13}, 12)
            with self.assertRaises(HTTPException) as actualizar_error:
                perfil_service.actualizar_perfil(None, 13, {"nombre_usuario": "X"}, 12)
        self.assertEqual(crear_error.exception.status_code, 403)
        self.assertEqual(actualizar_error.exception.status_code, 403)
        crear.assert_not_called()
        obtener.assert_not_called()

    def test_propietario_puede_actualizar_su_perfil(self):
        perfil = SimpleNamespace(id_usuario=12)
        with (
            patch.object(perfil_service.repo, "get_perfil_by_usuario", return_value=perfil),
            patch.object(perfil_service.repo, "update_perfil", return_value=perfil) as actualizar,
        ):
            resultado = perfil_service.actualizar_perfil(
                None, 12, {"nombre_usuario": "Propio"}, 12
            )
        self.assertIs(resultado, perfil)
        actualizar.assert_called_once()

    def test_usuario_puede_crear_su_perfil_con_su_propio_id(self):
        perfil = SimpleNamespace(id_usuario=12)
        with (
            patch.object(perfil_service.repo, "get_perfil_by_usuario", return_value=None),
            patch.object(perfil_service.repo, "create_perfil", return_value=perfil) as crear,
        ):
            resultado = perfil_service.crear_perfil(
                None, {"id_usuario": 12, "nombre_usuario": "Propio"}, 12
            )
        self.assertIs(resultado, perfil)
        self.assertEqual(crear.call_args.args[1]["id_usuario"], 12)

    def test_sesion_se_inicia_con_identidad_del_actor_y_tarea_autorizada(self):
        sesion = SimpleNamespace(id_usuario=12, id_tarea=4)
        with (
            patch.object(tarea_service, "verificar_permiso_tarea") as verificar,
            patch.object(sesion_cronometro_service.repo, "get_sesion_activa", return_value=None),
            patch.object(sesion_cronometro_service.repo, "create_sesion", return_value=sesion) as crear,
        ):
            resultado = sesion_cronometro_service.iniciar_sesion(None, 12, 4)
        self.assertIs(resultado, sesion)
        verificar.assert_called_once_with(None, 4, 12, "cronometro")
        self.assertEqual(crear.call_args.args[1]["id_usuario"], 12)

    def test_usuario_no_puede_finalizar_ni_listar_sesiones_ajenas(self):
        sesion = SimpleNamespace(id_usuario=13, fecha_fin=None)
        with (
            patch.object(sesion_cronometro_service.repo, "get_sesion_by_id", return_value=sesion),
            patch.object(sesion_cronometro_service.repo, "update_sesion") as actualizar,
            patch.object(sesion_cronometro_service.repo, "get_sesiones_by_usuario") as listar,
        ):
            with self.assertRaises(HTTPException) as finalizar_error:
                sesion_cronometro_service.finalizar_sesion(None, 5, 12)
            with self.assertRaises(HTTPException) as listar_error:
                sesion_cronometro_service.listar_sesiones_usuario(None, 13, 12)
        self.assertEqual(finalizar_error.exception.status_code, 404)
        self.assertEqual(listar_error.exception.status_code, 404)
        actualizar.assert_not_called()
        listar.assert_not_called()

    def test_propietario_puede_finalizar_y_listar_sus_sesiones(self):
        inicio = datetime.utcnow() - timedelta(minutes=5)
        sesion = SimpleNamespace(id_usuario=12, fecha_inicio=inicio, fecha_fin=None)
        finalizada = SimpleNamespace(id_usuario=12, fecha_inicio=inicio, fecha_fin=datetime.utcnow())
        with (
            patch.object(sesion_cronometro_service.repo, "get_sesion_by_id", return_value=sesion),
            patch.object(sesion_cronometro_service.repo, "update_sesion", return_value=finalizada) as actualizar,
            patch.object(sesion_cronometro_service.repo, "get_sesiones_by_usuario", return_value=[finalizada]) as listar,
        ):
            self.assertIs(sesion_cronometro_service.finalizar_sesion(None, 5, 12), finalizada)
            self.assertEqual(sesion_cronometro_service.listar_sesiones_usuario(None, 12, 12), [finalizada])
        actualizar.assert_called_once()
        listar.assert_called_once_with(None, 12)


class ConsultasTareaAisladasTests(unittest.TestCase):
    def test_listado_y_calendario_filtran_a_tareas_del_usuario_y_sus_grupos(self):
        engine = create_engine("sqlite:///:memory:")
        tablas = [
            Usuario.__table__,
            Categoria.__table__,
            Grupo.__table__,
            Tarea.__table__,
            Integrante.__table__,
        ]
        Base.metadata.create_all(engine, tables=tablas)
        try:
            with SQLSession(engine) as db:
                db.add_all(
                    [
                        Usuario(id_usuario=12, correo_electronico="uno@example.test", contrasena="hash"),
                        Usuario(id_usuario=13, correo_electronico="dos@example.test", contrasena="hash"),
                        Categoria(id_categoria=1, nombre_categoria="Sintética"),
                        Grupo(id_grupo=7, nombre_grupo="Grupo uno", codigo_acceso="ABC12345"),
                        Grupo(id_grupo=8, nombre_grupo="Grupo dos", codigo_acceso="DEF12345"),
                    ]
                )
                db.flush()
                db.add_all(
                    [
                        Integrante(id_usuario=12, id_grupo=7, rol="lider"),
                        Integrante(id_usuario=13, id_grupo=8, rol="lider"),
                        Tarea(
                            id_tarea=1,
                            nombre="Personal propia",
                            fecha_entrega=datetime(2026, 10, 20),
                            dificultad_estimada=2,
                            tiempo_estimado=30,
                            id_categoria=1,
                            id_usuario=12,
                        ),
                        Tarea(
                            id_tarea=2,
                            nombre="Personal ajena",
                            fecha_entrega=datetime(2026, 10, 20),
                            dificultad_estimada=2,
                            tiempo_estimado=30,
                            id_categoria=1,
                            id_usuario=13,
                        ),
                        Tarea(
                            id_tarea=3,
                            nombre="Compartida propia",
                            fecha_entrega=datetime(2026, 10, 20),
                            dificultad_estimada=2,
                            tiempo_estimado=30,
                            id_categoria=1,
                            id_grupo=7,
                        ),
                        Tarea(
                            id_tarea=4,
                            nombre="Compartida ajena",
                            fecha_entrega=datetime(2026, 10, 20),
                            dificultad_estimada=2,
                            tiempo_estimado=30,
                            id_categoria=1,
                            id_grupo=8,
                        ),
                    ]
                )
                db.commit()

                listado = tarea_repository.obtener_tareas_visibles_para_usuario(db, 12)
                calendario = tarea_repository.obtener_tareas_por_rango(
                    db, date(2026, 10, 1), date(2026, 10, 31), 12
                )

                self.assertEqual({tarea.id_tarea for tarea in listado}, {1, 3})
                self.assertEqual({tarea.id_tarea for tarea in calendario}, {1, 3})
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
