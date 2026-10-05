from typing import List
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import requerir_admin
from app.models.usuario import Usuario
from app.models.integrante import Integrante
from app.schemas.grupo import IntegranteAdminResponse

router=APIRouter(prefix="/integrantes", tags=["Integrantes"])

@router.get("",response_model=list[IntegranteAdminResponse])
def listar_integrantes_admin(
    db:Session=Depends(get_db),
    admin:Usuario=Depends(requerir_admin),
):
    filas=(
        db.query(Integrante,Usuario.correo_electronico)
        .join(Usuario,Usuario.id_usuario==Integrante.id_usuario)
        .order_by(Integrante.id_integrante)
        .all()
    )
    return[
        IntegranteAdminResponse(
            id_integrante=i.id_integrante,
            id_usuario=i.id_usuario,
            id_grupo=i.id_grupo,
            correo_electronico=correo,
            rol=i.rol,
            fecha_ingreso=i.fecha_ingreso
        )
        for i,correo in filas
    ]