from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.estadistica_categoria import EstadisticaCategoriaOut
from app.services import estadistica_service as service

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])

@router.get("/me", response_model=List[EstadisticaCategoriaOut])
def mis_estadisticas_categoria(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return service.obtener_estadisticas_categoria_usuario(db, usuario.id_usuario)