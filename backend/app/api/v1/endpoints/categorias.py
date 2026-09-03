from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.categoria import CategoriaResponse
from app.services import categoria_service

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return categoria_service.listar_categorias(db)