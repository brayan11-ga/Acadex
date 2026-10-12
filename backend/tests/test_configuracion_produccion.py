import unittest

from pydantic import ValidationError

from app.config.settings import Settings


class ConfiguracionProduccionTests(unittest.TestCase):
    def crear_settings(self, **cambios):
        valores = {
            "_env_file": None,
            "db_user": "acadex",
            "db_password": "p@ss:/word%",
            "db_host": "db.example.test",
            "db_port": 5432,
            "db_name": "acadex",
            "secret_key": "clave-sintetica-con-longitud-suficiente-para-pruebas",
            "algorithm": "HS256",
            "access_token_expire_minutes": 30,
            **cambios,
        }
        return Settings(**valores)

    def test_url_postgresql_escapa_credenciales_y_expone_tls_separado(self):
        configuracion = self.crear_settings(
            db_sslmode="verify-full",
            db_sslrootcert="/certs/ca.pem",
        )

        self.assertEqual(configuracion.database_url.password, "p@ss:/word%")
        self.assertEqual(configuracion.database_url.host, "db.example.test")
        self.assertEqual(
            configuracion.database_connect_args,
            {"sslmode": "verify-full", "sslrootcert": "/certs/ca.pem"},
        )

    def test_rechaza_cors_con_comodin_o_ruta(self):
        for origen in ("*", "https://acadex.example.com/app"):
            with self.subTest(origen=origen), self.assertRaises(ValidationError):
                self.crear_settings(cors_origins=origen)

    def test_produccion_exige_origen_https_y_tls_postgresql(self):
        base = {
            "app_env": "production",
            "cors_origins": "https://acadex.pages.dev",
        }
        with self.assertRaises(RuntimeError):
            self.crear_settings(**base, db_sslmode="prefer").validar_configuracion_produccion()

        configuracion = self.crear_settings(**base, db_sslmode="require")
        self.assertEqual(configuracion.allowed_origins, ["https://acadex.pages.dev"])
        configuracion.validar_configuracion_produccion()

if __name__ == "__main__":
    unittest.main()
