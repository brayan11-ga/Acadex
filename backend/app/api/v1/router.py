# backend/app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import (
    usuarios,
    perfiles,
    tareas,
    sesiones_cronometro,
    categorias,
    panel,
    estadisticas,
    grupos,
    admin,
    integrantes,
    notificaciones,
)

router = APIRouter(prefix="/api/v1")

router.include_router(usuarios.router)
router.include_router(perfiles.router)
router.include_router(tareas.router)
router.include_router(sesiones_cronometro.router)
router.include_router(categorias.router)
router.include_router(panel.router)
router.include_router(estadisticas.router)
router.include_router(grupos.router)
router.include_router(integrantes.router)
router.include_router(admin.router)
router.include_router(notificaciones.router)