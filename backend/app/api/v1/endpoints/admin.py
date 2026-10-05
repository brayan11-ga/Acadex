from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import requerir_admin
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.grupo import Grupo
from app.models.tarea import Tarea
from app.models.integrante import Integrante

router= APIRouter(prefix="/admin",tags=["Admin"])

class ResumenAdmin(BaseModel):
    usuarios: int
    categorias: int
    grupos: int
    tareas:int
    integrantes:int

@router.get("/resumen", response_model=ResumenAdmin)
def obtener_resumen(
    db: Session=Depends(get_db),
    admin: Usuario=Depends(requerir_admin),
):

    def contar(columna)-> int:
        return db.query(func.count(columna)).scalar() or 0

    return ResumenAdmin(
        usuarios=contar(Usuario.id_usuario),
        categorias=contar(Categoria.id_categoria),
        grupos=contar(Grupo.id_grupo),
        tareas=contar(Tarea.id_tarea),
        integrantes=contar(Integrante.id_integrante),
    )
