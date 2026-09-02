# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import usuarios, perfiles, tareas, sesiones_cronometro, categorias

router = APIRouter(prefix="/api/v1")

router.include_router(usuarios.router)
router.include_router(perfiles.router)
router.include_router(tareas.router)
router.include_router(sesiones_cronometro.router)
router.include_router(categorias.router)