from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
# Asegúrate de importar tu dependencia real de autenticación (ajusta la ruta según tu estructura)
from app.dependencies.auth import get_current_user 

from app.services.estadisticas_service import obtener_resumen_estadisticas
from app.schemas.estadisticas_schema import ResumenEstadisticasResponse

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas Dashboard"])

@router.get("/resumen", response_model=ResumenEstadisticasResponse)
def obtener_resumen_dashboard(
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_current_user)  # <-- Se coloca aquí dentro como parámetro de la función
):
    """
    Obtiene el resumen dinámico de estadísticas del usuario autenticado.
    """
    # Extraemos el ID real del usuario logueado a través del token JWT
    id_usuario = usuario_actual.id_usuario  # O usuario_actual.id según tu modelo
    
    return obtener_resumen_estadisticas(db, id_usuario)