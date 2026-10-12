# app/main.py
import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import router
import app.models  # noqa
from app.config.settings import settings
from app.db.session import engine

settings.validar_configuracion_produccion()

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
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        logging.getLogger(__name__).warning("La comprobación de PostgreSQL no está disponible")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
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
