# backend/app/api/v1/endpoints/grupos.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.auth import get_usuario_actual, requerir_lider_de_grupo
from app.models.usuario import Usuario
from app.schemas.grupo import (
    GrupoCreate,
    GrupoResponse,
    GrupoConRolResponse,
    GrupoJoinRequest,
    IntegranteResponse,
)
from app.services import grupo_service

router = APIRouter(prefix="/grupos", tags=["Grupos"])


@router.get("/mis-grupos", response_model=List[GrupoConRolResponse])
def listar_mis_grupos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return grupo_service.listar_grupos_de_usuario(db, usuario.id_usuario)


@router.post("/", response_model=GrupoResponse, status_code=status.HTTP_201_CREATED)
def crear_grupo(
    datos: GrupoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return grupo_service.crear_grupo(db, datos.nombre_grupo, datos.descripcion, usuario.id_usuario)


@router.post("/unirse", response_model=IntegranteResponse, status_code=status.HTTP_201_CREATED)
def unirse_a_grupo(
    datos: GrupoJoinRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    integrante = grupo_service.unirse_a_grupo(db, datos.codigo_acceso, usuario.id_usuario)
    return {
        "id_integrante": integrante.id_integrante,
        "id_usuario": integrante.id_usuario,
        "correo_electronico": usuario.correo_electronico,
        "rol": integrante.rol,
        "fecha_ingreso": integrante.fecha_ingreso,
    }


@router.get("/{id_grupo}/integrantes", response_model=List[IntegranteResponse])
def listar_integrantes(
    id_grupo: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return grupo_service.listar_integrantes_de_grupo(db, id_grupo, usuario.id_usuario)


@router.delete("/{id_grupo}/salir", status_code=status.HTTP_204_NO_CONTENT)
def salir_de_grupo(
    id_grupo: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    grupo_service.abandonar_grupo(db, id_grupo, usuario.id_usuario)


@router.delete("/{id_grupo}/integrantes/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def expulsar_integrante(
    id_grupo: int,
    id_usuario: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_lider_de_grupo),
):
    grupo_service.expulsar_integrante(db, id_grupo, id_usuario)


@router.delete("/{id_grupo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_grupo(
    id_grupo: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(requerir_lider_de_grupo),
):
    grupo_service.eliminar_grupo(db, id_grupo)