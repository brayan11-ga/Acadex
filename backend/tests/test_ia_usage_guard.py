import unittest
from datetime import date, timedelta
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.ia_usage_guard import (
    bloquear_hasta_reinicio_cuota_google,
    consumir_cupo_analisis,
    liberar_cupo_usuario_analisis,
    proximo_reinicio_cuota_google,
    verificar_bloqueo_cuota_google,
)
from app.models.bloqueo_cuota_gemini import BloqueoCuotaGemini
from app.models.uso_analisis_ia import UsoAnalisisIA


class LimitesUsoGeminiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        UsoAnalisisIA.__table__.create(self.engine)
        BloqueoCuotaGemini.__table__.create(self.engine)
        self.db = Session(self.engine)
        self.hoy = date(2026, 10, 12)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _cantidad(self, alcance: str, identificador: str, fecha: date | None = None):
        clave = fecha or self.hoy
        registro = self.db.get(
            UsoAnalisisIA, (clave, alcance, identificador)
        )
        return registro.cantidad if registro else 0

    def test_aplica_tres_analisis_diarios_por_usuario(self):
        for _ in range(3):
            consumir_cupo_analisis(
                self.db,
                41,
                fecha_utc=self.hoy,
                limite_usuario=3,
                limite_global=90,
            )

        with self.assertRaises(HTTPException) as error:
            consumir_cupo_analisis(
                self.db,
                41,
                fecha_utc=self.hoy,
                limite_usuario=3,
                limite_global=90,
            )

        self.assertEqual(error.exception.status_code, 429)
        self.assertEqual(self._cantidad("usuario", "41"), 3)
        self.assertEqual(self._cantidad("global", "global"), 3)

    def test_limite_global_no_consume_el_cupo_personal_si_se_agota(self):
        consumir_cupo_analisis(
            self.db,
            41,
            fecha_utc=self.hoy,
            limite_usuario=3,
            limite_global=1,
        )

        with self.assertRaises(HTTPException) as error:
            consumir_cupo_analisis(
                self.db,
                42,
                fecha_utc=self.hoy,
                limite_usuario=3,
                limite_global=1,
            )

        self.assertEqual(error.exception.status_code, 429)
        self.assertEqual(self._cantidad("usuario", "42"), 0)
        self.assertEqual(self._cantidad("global", "global"), 1)

    def test_limites_se_reinician_al_cambiar_el_dia_utc(self):
        consumir_cupo_analisis(
            self.db,
            41,
            fecha_utc=self.hoy,
            limite_usuario=1,
            limite_global=1,
        )
        manana = self.hoy + timedelta(days=1)

        consumir_cupo_analisis(
            self.db,
            41,
            fecha_utc=manana,
            limite_usuario=1,
            limite_global=1,
        )

        self.assertEqual(self._cantidad("usuario", "41", self.hoy), 1)
        self.assertEqual(self._cantidad("usuario", "41", manana), 1)

    def test_expira_contadores_de_mas_de_treinta_dias(self):
        antiguo = self.hoy - timedelta(days=31)
        self.db.add(
            UsoAnalisisIA(
                fecha_utc=antiguo,
                alcance="usuario",
                identificador_alcance="41",
                cantidad=1,
            )
        )
        self.db.commit()

        consumir_cupo_analisis(
            self.db,
            42,
            fecha_utc=self.hoy,
            limite_usuario=3,
            limite_global=90,
        )

        self.assertEqual(self._cantidad("usuario", "41", antiguo), 0)
        self.assertEqual(
            self.db.scalar(select(UsoAnalisisIA).where(UsoAnalisisIA.fecha_utc == self.hoy)).cantidad,
            1,
        )

    def test_falla_cerrado_si_no_se_aplico_la_migracion(self):
        UsoAnalisisIA.__table__.drop(self.engine)

        with self.assertRaises(HTTPException) as error:
            consumir_cupo_analisis(
                self.db,
                41,
                fecha_utc=self.hoy,
                limite_usuario=3,
                limite_global=90,
            )

        self.assertEqual(error.exception.status_code, 503)

    def test_reinicio_de_google_es_medianoche_del_pacifico(self):
        ahora = datetime(2026, 10, 12, 14, 30, tzinfo=timezone.utc)

        self.assertEqual(
            proximo_reinicio_cuota_google(ahora),
            datetime(2026, 10, 13, 7, 0, tzinfo=timezone.utc),
        )

    def test_bloqueo_por_cuota_diaria_persiste_hasta_el_reinicio(self):
        ahora = datetime(2026, 10, 12, 14, 30, tzinfo=timezone.utc)
        reinicio = bloquear_hasta_reinicio_cuota_google(self.db, ahora=ahora)
        bloquear_hasta_reinicio_cuota_google(
            self.db,
            ahora=datetime(2026, 10, 11, 14, 30, tzinfo=timezone.utc),
        )
        guardado = self.db.get(BloqueoCuotaGemini, "proyecto")
        self.assertEqual(guardado.bloqueado_hasta, reinicio.replace(tzinfo=None))

        with self.assertRaises(HTTPException) as error:
            verificar_bloqueo_cuota_google(
                self.db, ahora=datetime(2026, 10, 13, 6, 59, tzinfo=timezone.utc)
            )

        self.assertEqual(error.exception.status_code, 429)
        self.assertEqual(error.exception.headers["Retry-After"], "60")
        verificar_bloqueo_cuota_google(self.db, ahora=reinicio)

    def test_error_de_proveedor_libera_cupo_personal_pero_no_global(self):
        consumir_cupo_analisis(
            self.db,
            41,
            fecha_utc=self.hoy,
            limite_usuario=1,
            limite_global=18,
        )

        liberar_cupo_usuario_analisis(self.db, 41, fecha_utc=self.hoy)

        self.assertEqual(self._cantidad("usuario", "41"), 0)
        self.assertEqual(self._cantidad("global", "global"), 1)

    def test_overrides_antiguos_no_superan_los_limites_del_plan_gratuito(self):
        with (
            patch("app.core.ia_usage_guard.settings.gemini_user_daily_limit", 3),
            patch("app.core.ia_usage_guard.settings.gemini_global_daily_limit", 90),
        ):
            consumir_cupo_analisis(
                self.db,
                41,
                fecha_utc=self.hoy,
                fecha_global=self.hoy,
            )
            with self.assertRaises(HTTPException) as error_personal:
                consumir_cupo_analisis(
                    self.db,
                    41,
                    fecha_utc=self.hoy,
                    fecha_global=self.hoy,
                )

            for id_usuario in range(42, 61):
                consumir_cupo_analisis(
                    self.db,
                    id_usuario,
                    fecha_utc=self.hoy,
                    fecha_global=self.hoy,
                )

            with self.assertRaises(HTTPException) as error_global:
                consumir_cupo_analisis(
                    self.db,
                    61,
                    fecha_utc=self.hoy,
                    fecha_global=self.hoy,
                )

        self.assertEqual(error_personal.exception.status_code, 429)
        self.assertEqual(error_global.exception.status_code, 429)
        self.assertEqual(self._cantidad("global", "global"), 20)


if __name__ == "__main__":
    unittest.main()
