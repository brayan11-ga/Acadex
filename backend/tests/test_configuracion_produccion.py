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
            "attachments_enabled": True,
            "attachments_storage_backend": "supabase",
            "supabase_url": "https://acadex-demo.supabase.co",
            "supabase_service_role_key": "clave-falsa-de-prueba-no-utilizable",
        }
        with self.assertRaises(RuntimeError):
            self.crear_settings(**base, db_sslmode="prefer").validar_configuracion_produccion()

        configuracion = self.crear_settings(**base, db_sslmode="require")
        self.assertEqual(configuracion.allowed_origins, ["https://acadex.pages.dev"])
        configuracion.validar_configuracion_produccion()

    def test_produccion_no_permite_adjuntos_sobre_disco_local(self):
        configuracion = self.crear_settings(
            app_env="production",
            cors_origins="https://acadex.pages.dev",
            db_sslmode="require",
            attachments_enabled=True,
        )
        with self.assertRaisesRegex(RuntimeError, "ATTACHMENTS_STORAGE_BACKEND=supabase"):
            configuracion.validar_configuracion_produccion()

    def test_produccion_no_arranca_sin_guardado_de_adjuntos_habilitado(self):
        configuracion = self.crear_settings(
            app_env="production",
            cors_origins="https://acadex.pages.dev",
            db_sslmode="require",
            attachments_enabled=False,
        )
        with self.assertRaisesRegex(RuntimeError, "ATTACHMENTS_ENABLED=true"):
            configuracion.validar_configuracion_produccion()

    def test_produccion_exige_storage_supabase_privado_configurado(self):
        base = {
            "app_env": "production",
            "cors_origins": "https://acadex.pages.dev",
            "db_sslmode": "require",
            "attachments_enabled": True,
            "attachments_storage_backend": "supabase",
            "supabase_url": "https://acadex-demo.supabase.co",
            "supabase_storage_bucket": "acadex-adjuntos",
        }
        with self.assertRaisesRegex(RuntimeError, "SUPABASE_SERVICE_ROLE_KEY"):
            self.crear_settings(**base).validar_configuracion_produccion()

        configuracion = self.crear_settings(
            **base,
            supabase_service_role_key="clave-falsa-de-prueba-no-utilizable",
        )
        configuracion.validar_configuracion_produccion()

        con_clave_actual = self.crear_settings(
            **base,
            supabase_secret_key="sb_secret_clave-falsa-de-prueba",
        )
        con_clave_actual.validar_configuracion_produccion()

    def test_rechaza_nombres_de_bucket_no_seguros(self):
        with self.assertRaises(ValidationError):
            self.crear_settings(supabase_storage_bucket="../bucket")

if __name__ == "__main__":
    unittest.main()
