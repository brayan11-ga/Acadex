from typing import List
from sqlalchemy.orm import Session

from app.models.categoria import Categoria


def obtener_todas_las_categorias(db: Session) -> List[Categoria]:
    return db.query(Categoria).all()