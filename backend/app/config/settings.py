from urllib.parse import urlsplit

from pydantic import field_validator
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

    app_env: str = "development"
    cors_origins: str = "http://localhost:5173"
    frontend_url: str = "http://localhost:5173"

    password_reset_enabled: bool = False
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
