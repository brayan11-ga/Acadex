# app/main.py
import logging

from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import router
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa
from app.config.settings import settings
from app.db.session import engine
from app.services import supabase_storage

settings.validar_configuracion_produccion()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


api = FastAPI(title="Acadex API", lifespan=lifespan)

api.include_router(router)

api = FastAPI(title="Acadex API")

api.include_router(router)


@api.get("/")
def root():
    return {"mensaje": "Acadex funcionando"}


@api.get("/health/live", include_in_schema=False)
def health_live():
    return {"status": "ok"}


@api.get("/health/ready", include_in_schema=False)
def health_ready():
    try:
        with engine.connect() as connection:
            esquema_listo = connection.execute(text("""
                SELECT
                    to_regclass('public.limites_solicitud') IS NOT NULL
                    AND to_regclass('public.uso_analisis_ia') IS NOT NULL
                    AND to_regclass('public.bloqueo_cuota_gemini') IS NOT NULL
                    AND EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = 'usuarios'
                          AND column_name = 'bloqueado_hasta'
                    )
                    AND EXISTS (
                        SELECT 1 FROM pg_index
                        WHERE indexrelid = to_regclass('public.uq_sesiones_tarea_activa')
                          AND indisunique
                    )
            """)).scalar_one()
            if not esquema_listo:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Faltan migraciones obligatorias de seguridad",
                )
    except SQLAlchemyError as error:
        logging.getLogger(__name__).warning("La comprobación de PostgreSQL no está disponible")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        ) from error
    if settings.attachments_enabled and settings.attachments_storage_backend == "supabase":
        try:
            supabase_storage.validar_bucket_privado()
        except supabase_storage.SupabaseStorageError as error:
            logging.getLogger(__name__).warning("El bucket privado de adjuntos no está disponible")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Almacenamiento privado de adjuntos no disponible",
            ) from error
    return {"status": "ok"}


# Wrap the whole application so CORS headers are also added to unhandled
# error responses produced by FastAPI/Starlette's outer error middleware.
app = CORSMiddleware(
    app=api,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
