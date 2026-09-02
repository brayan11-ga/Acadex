from typing import List
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.repositories import categoria_repository


def listar_categorias(db: Session) -> List[Categoria]:
    return categoria_repository.obtener_todas_las_categorias(db)