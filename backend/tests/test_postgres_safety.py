"""Pruebas unitarias de las guardas PostgreSQL sin una base real."""

import os
import socket
import subprocess
import sys
import unittest
import builtins
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import Mock, patch

from app.testing.postgres_safety import (
    TEST_DATABASE_NAME,
    UnsafeTestDatabaseError,
    crear_engine_pruebas,
    crear_esquema_pruebas,
    eliminar_esquema_pruebas,
    validar_configuracion_pruebas,
)


class _Result:
    def __init__(self, value):
        self.value = value

    def scalar_one(self):
        return self.value


class _Connection:
    def __init__(self, engine):
        self.engine = engine

    def execute(self, statement):
        sql = str(statement)
        self.engine.statements.append(sql)
        if sql == "SELECT current_database()":
            return _Result(self.engine.actual_database)
        return _Result(None)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class _Engine:
    def __init__(self, actual_database):
        self.actual_database = actual_database
        self.statements = []
        self.begin_calls = 0

    def connect(self):
        return _Connection(self)

    @contextmanager
    def begin(self):
        self.begin_calls += 1
        yield _Connection(self)


class PostgresSafetyTests(unittest.TestCase):
    schema_name = "acadex_test_" + ("a" * 32)

    def _environment(self, **overrides):
        environment = {
            "ACADEX_RUN_POSTGRES_TESTS": "1",
            "ACADEX_TEST_DB_NAME": TEST_DATABASE_NAME,
            "ACADEX_TEST_DB_TARGET": "compose",
            "ACADEX_TEST_DB_HOST": "db",
            "ACADEX_TEST_DB_PORT": "5432",
            "ACADEX_TEST_DB_USER": "acadex_test_runner",
            "ACADEX_TEST_DB_PASSWORD": "unit-test-only",
            "ACADEX_TEST_COMPOSE_PROJECT": "acadex-test-1234abcd",
            "COMPOSE_PROJECT_NAME": "acadex-test-1234abcd",
            "DB_HOST": "db",
            "DB_PORT": "5432",
            "DB_NAME": TEST_DATABASE_NAME,
        }
        environment.update(overrides)
        return environment

    def _assert_rejected_before_engine(self, environment):
        engine_factory = Mock(side_effect=AssertionError("no se debe crear un engine"))
        with self.assertRaises(UnsafeTestDatabaseError):
            crear_engine_pruebas(
                environment,
                engine_factory,
                en_contenedor=True,
                marcador_aislamiento_presente=True,
            )
        engine_factory.assert_not_called()

    def test_sin_opt_in_no_crea_engine(self):
        for opt_in in (None, "0"):
            with self.subTest(opt_in=opt_in):
                environment = self._environment()
                if opt_in is None:
                    del environment["ACADEX_RUN_POSTGRES_TESTS"]
                else:
                    environment["ACADEX_RUN_POSTGRES_TESTS"] = opt_in
                self._assert_rejected_before_engine(environment)

    def test_nombre_incorrecto_se_rechaza_antes_de_crear_engine(self):
        environment = self._environment(ACADEX_TEST_DB_NAME="acadex_dev")
        self._assert_rejected_before_engine(environment)

    def test_host_remoto_se_rechaza_antes_de_crear_engine(self):
        environment = self._environment(
            ACADEX_TEST_DB_HOST="project.supabase.co",
            DB_HOST="project.supabase.co",
        )
        self._assert_rejected_before_engine(environment)

    def test_configuracion_ausente_o_contradictoria_se_rechaza_antes_del_engine(self):
        for variable in (
            "ACADEX_TEST_DB_USER",
            "ACADEX_TEST_DB_PASSWORD",
            "ACADEX_TEST_DB_TARGET",
            "ACADEX_TEST_DB_PORT",
            "ACADEX_TEST_COMPOSE_PROJECT",
            "COMPOSE_PROJECT_NAME",
        ):
            with self.subTest(variable=variable):
                missing = self._environment()
                del missing[variable]
                self._assert_rejected_before_engine(missing)

        for variable, value in (
            ("DB_NAME", "acadex_dev"),
            ("DB_USER", "otro_usuario"),
            ("DB_PASSWORD", "otra_credencial"),
            ("PGHOST", "servidor-remoto.example"),
            ("COMPOSE_PROJECT_NAME", "acadex-dev"),
        ):
            with self.subTest(variable=variable):
                self._assert_rejected_before_engine(
                    self._environment(**{variable: value})
                )

    def test_contexto_compose_incorrecto_se_rechaza_antes_del_engine(self):
        for overrides in (
            {"ACADEX_TEST_DB_TARGET": "host"},
            {"ACADEX_TEST_DB_HOST": "127.0.0.1"},
            {"ACADEX_TEST_DB_PORT": "55433"},
        ):
            with self.subTest(overrides=overrides):
                self._assert_rejected_before_engine(self._environment(**overrides))

    def test_contexto_operativo_ausente_bloquea_engine_aunque_configuracion_sea_valida(self):
        environment = self._environment()
        engine_factory = Mock()

        with self.assertRaises(UnsafeTestDatabaseError):
            crear_engine_pruebas(
                environment,
                engine_factory,
                en_contenedor=True,
                marcador_aislamiento_presente=False,
            )

        engine_factory.assert_not_called()

    def test_contexto_operativo_ambiguo_o_fuera_de_compose_bloquea_engine(self):
        cases = (
            (self._environment(ACADEX_TEST_RUNNER_CONTEXT="host"), True, True),
            (self._environment(ACADEX_TEST_RUNNER_CONTEXT="isolated-compose"), False, True),
            (self._environment(ACADEX_TEST_RUNNER_CONTEXT="isolated-compose"), True, False),
        )
        for environment, en_contenedor, marcador in cases:
            with self.subTest(en_contenedor=en_contenedor, marcador=marcador):
                engine_factory = Mock()
                with self.assertRaises(UnsafeTestDatabaseError):
                    crear_engine_pruebas(
                        environment,
                        engine_factory,
                        en_contenedor=en_contenedor,
                        marcador_aislamiento_presente=marcador,
                    )
                engine_factory.assert_not_called()

    def test_configuracion_compose_valida_se_acepta_sin_abrir_conexion(self):
        environment = self._environment()
        engine_factory = Mock()
        real_import = builtins.__import__

        def import_sin_sqlalchemy(name, *args, **kwargs):
            if name == "sqlalchemy" or name.startswith("sqlalchemy."):
                raise AssertionError("la validación no debe importar SQLAlchemy")
            return real_import(name, *args, **kwargs)

        with (
            patch("builtins.__import__", side_effect=import_sin_sqlalchemy),
            patch.object(socket, "socket", side_effect=AssertionError("socket inesperado")),
            patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS inesperado")),
        ):
            config = validar_configuracion_pruebas(environment)

        self.assertEqual(config.database, TEST_DATABASE_NAME)
        self.assertEqual(config.host, "db")
        self.assertEqual(config.port, 5432)
        engine_factory.assert_not_called()

    def test_importar_el_modulo_puro_no_carga_sesion_main_ni_sqlalchemy(self):
        script = "\n".join(
            (
                "import sys",
                "import app.testing.postgres_safety",
                "for name in ('app.db.session', 'app.main', 'app.config.settings', 'sqlalchemy'):",
                "    assert name not in sys.modules, name",
            )
        )
        backend_dir = Path(__file__).resolve().parents[1]

        subprocess.run(
            [sys.executable, "-c", script],
            cwd=backend_dir,
            env=os.environ.copy(),
            check=True,
            capture_output=True,
            text=True,
        )

    def test_variables_de_url_alternativas_se_rechazan(self):
        for variable in ("DATABASE_URL", "DATABASES_URL"):
            with self.subTest(variable=variable):
                self._assert_rejected_before_engine(self._environment(**{variable: "configured"}))

    def _crear(self, engine, *, configured, expected=TEST_DATABASE_NAME, opt_in="1"):
        crear_esquema_pruebas(
            engine,
            self.schema_name,
            configured_database=configured,
            expected_database=expected,
            run_postgres_tests=opt_in,
        )

    def test_base_de_desarrollo_se_rechaza_antes_de_cualquier_ddl(self):
        engine = _Engine("acadex_dev")

        with self.assertRaises(UnsafeTestDatabaseError):
            self._crear(engine, configured="acadex_dev")

        self.assertEqual(engine.begin_calls, 0)
        self.assertFalse(any("CREATE " in sql or "DROP " in sql for sql in engine.statements))

    def test_nombre_configurado_no_coincidente_se_rechaza_antes_de_ddl(self):
        engine = _Engine(TEST_DATABASE_NAME)

        with self.assertRaises(UnsafeTestDatabaseError):
            self._crear(engine, configured="acadex_dev")

        self.assertEqual(engine.begin_calls, 0)
        self.assertFalse(any("CREATE " in sql or "DROP " in sql for sql in engine.statements))

    def test_sin_confirmacion_explicita_se_rechaza_antes_de_ddl(self):
        engine = _Engine(TEST_DATABASE_NAME)

        with self.assertRaises(UnsafeTestDatabaseError):
            self._crear(engine, configured=TEST_DATABASE_NAME, opt_in=None)

        self.assertEqual(engine.begin_calls, 0)
        self.assertFalse(any("CREATE " in sql or "DROP " in sql for sql in engine.statements))

    def test_base_no_autorizada_se_rechaza_antes_de_eliminar_esquema(self):
        engine = _Engine("acadex_dev")

        with self.assertRaises(UnsafeTestDatabaseError):
            eliminar_esquema_pruebas(
                engine,
                self.schema_name,
                configured_database="acadex_dev",
                expected_database=TEST_DATABASE_NAME,
                run_postgres_tests="1",
            )

        self.assertEqual(engine.begin_calls, 0)
        self.assertFalse(any("CREATE " in sql or "DROP " in sql for sql in engine.statements))

    def test_nombre_esperado_debe_ser_explicito_y_exactamente_acadex_test(self):
        engine = _Engine(TEST_DATABASE_NAME)

        with self.assertRaises(UnsafeTestDatabaseError):
            self._crear(engine, configured=TEST_DATABASE_NAME, expected="test")

        self.assertEqual(engine.begin_calls, 0)

    def test_esquema_no_autorizado_se_rechaza_sin_consultar_ni_modificar(self):
        engine = _Engine(TEST_DATABASE_NAME)

        with self.assertRaises(UnsafeTestDatabaseError):
            crear_esquema_pruebas(
                engine,
                'acadex_test_x"; DROP SCHEMA public CASCADE; --',
                configured_database=TEST_DATABASE_NAME,
                expected_database=TEST_DATABASE_NAME,
                run_postgres_tests="1",
            )

        self.assertEqual(engine.statements, [])
        self.assertEqual(engine.begin_calls, 0)

    def test_destino_autorizado_solo_crea_y_elimina_el_esquema_aislado(self):
        engine = _Engine(TEST_DATABASE_NAME)
        self._crear(engine, configured=TEST_DATABASE_NAME)
        eliminar_esquema_pruebas(
            engine,
            self.schema_name,
            configured_database=TEST_DATABASE_NAME,
            expected_database=TEST_DATABASE_NAME,
            run_postgres_tests="1",
        )

        ddl = [sql for sql in engine.statements if sql.startswith(("CREATE ", "DROP "))]
        self.assertEqual(
            ddl,
            [
                f'CREATE SCHEMA "{self.schema_name}"',
                f'DROP SCHEMA "{self.schema_name}" CASCADE',
            ],
        )


if __name__ == "__main__":
    unittest.main()
