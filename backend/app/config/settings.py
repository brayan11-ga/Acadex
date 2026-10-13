import re
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_sslmode: str = "prefer"
    db_sslrootcert: str | None = None

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    gemini_api_key: str = ""
    # Defaults conservadores para el plan gratuito. Los límites efectivos se
    # acotan también en ia_usage_guard para tolerar overrides antiguos del .env.
    gemini_user_daily_limit: int = Field(default=1, ge=1, le=5)
    gemini_global_daily_limit: int = Field(default=18, ge=1, le=150)

    app_env: str = "development"
    cors_origins: str = "http://localhost:5173"
    frontend_url: str = "http://localhost:5173"

    password_reset_enabled: bool = False
    attachments_enabled: bool = False
    attachments_storage_backend: str = "local"
    supabase_url: str = ""
    supabase_secret_key: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "acadex-adjuntos"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = True
    mail_from: str = ""

    @field_validator("app_env")
    @classmethod
    def validar_entorno(cls, value: str) -> str:
        normalizado = value.strip().lower()
        if normalizado not in {"development", "test", "production"}:
            raise ValueError("APP_ENV debe ser development, test o production")
        return normalizado

    @field_validator("db_sslmode")
    @classmethod
    def validar_modo_ssl(cls, value: str) -> str:
        permitidos = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
        normalizado = value.strip().lower()
        if normalizado not in permitidos:
            raise ValueError("DB_SSLMODE no es un modo SSL de PostgreSQL válido")
        return normalizado

    @field_validator("attachments_storage_backend")
    @classmethod
    def validar_backend_adjuntos(cls, value: str) -> str:
        normalizado = value.strip().lower()
        if normalizado not in {"local", "supabase"}:
            raise ValueError("ATTACHMENTS_STORAGE_BACKEND debe ser local o supabase")
        return normalizado

    @field_validator("supabase_storage_bucket")
    @classmethod
    def validar_bucket_supabase(cls, value: str) -> str:
        normalizado = value.strip()
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,62}", normalizado):
            raise ValueError("SUPABASE_STORAGE_BUCKET debe ser un nombre de bucket válido")
        return normalizado

    @field_validator("cors_origins")
    @classmethod
    def validar_origenes_cors(cls, value: str) -> str:
        origenes = [origen.strip().rstrip("/") for origen in value.split(",") if origen.strip()]
        if not origenes or "*" in origenes:
            raise ValueError("CORS_ORIGINS debe listar orígenes explícitos; no se permite '*'")
        for origen in origenes:
            parsed = urlsplit(origen)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path:
                raise ValueError("Cada CORS_ORIGINS debe ser un origen HTTP(S), sin ruta")
        return ",".join(origenes)

    def validar_configuracion_produccion(self) -> None:
        if self.app_env.strip().lower() == "production":
            if len(self.secret_key) < 32:
                raise RuntimeError("Producción requiere una SECRET_KEY de al menos 32 caracteres")
            if any(not origen.startswith("https://") for origen in self.allowed_origins):
                raise RuntimeError("En producción, CORS_ORIGINS debe usar HTTPS")
            if self.db_sslmode not in {"require", "verify-ca", "verify-full"}:
                raise RuntimeError("En producción, DB_SSLMODE debe exigir TLS")
            if not self.attachments_enabled:
                raise RuntimeError("Producción requiere ATTACHMENTS_ENABLED=true para conservar los PDF de las tareas")
            parsed_storage_url = urlsplit(self.supabase_url.strip())
            if self.attachments_storage_backend != "supabase":
                raise RuntimeError(
                    "En producción, los adjuntos requieren ATTACHMENTS_STORAGE_BACKEND=supabase."
                )
            try:
                puerto_storage = parsed_storage_url.port
            except ValueError as error:
                raise RuntimeError("SUPABASE_URL no es válida") from error
            if (
                parsed_storage_url.scheme != "https"
                or not parsed_storage_url.hostname
                or puerto_storage is not None
                or parsed_storage_url.username
                or parsed_storage_url.password
                or parsed_storage_url.path not in {"", "/"}
                or parsed_storage_url.query
                or parsed_storage_url.fragment
            ):
                raise RuntimeError("SUPABASE_URL debe ser el origen HTTPS del proyecto Supabase")
            if not (self.supabase_secret_key.strip() or self.supabase_service_role_key.strip()):
                raise RuntimeError(
                    "Los adjuntos requieren SUPABASE_SECRET_KEY o SUPABASE_SERVICE_ROLE_KEY en el backend"
                )
            if not self.supabase_storage_bucket.strip():
                raise RuntimeError("Los adjuntos requieren SUPABASE_STORAGE_BUCKET")
            if self.password_reset_enabled:
                if not self.smtp_starttls:
                    raise RuntimeError("La recuperación de contraseña en producción requiere SMTP_STARTTLS")
                if not self.smtp_host or not self.mail_from:
                    raise RuntimeError("La recuperación de contraseña requiere SMTP_HOST y MAIL_FROM")
                if not self.frontend_url.startswith("https://"):
                    raise RuntimeError("La recuperación de contraseña requiere FRONTEND_URL con HTTPS")
                if bool(self.smtp_username) != bool(self.smtp_password):
                    raise RuntimeError("SMTP_USERNAME y SMTP_PASSWORD deben configurarse juntos")

    @property
    def allowed_origins(self) -> list[str]:
        return [origen for origen in self.cors_origins.split(",") if origen]

    @property
    def database_url(self) -> URL:
        # URL.create escapa correctamente contraseñas con @, :, / o caracteres similares.
        return URL.create(
            "postgresql+psycopg2",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

    @property
    def database_connect_args(self) -> dict[str, str]:
        args = {"sslmode": self.db_sslmode}
        if self.db_sslrootcert:
            args["sslrootcert"] = self.db_sslrootcert
        return args

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
