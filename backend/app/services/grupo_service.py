# backend/app/services/grupo_service.py
import secrets
import string
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.grupo import Grupo
from app.models.integrante import Integrante
from app.repositories import grupo_repository

ALFABETO_CODIGO = string.ascii_uppercase + string.digits
LONGITUD_CODIGO = 8


def _generar_codigo_acceso(db: Session) -> str:
    while True:
        codigo = "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(LONGITUD_CODIGO))
        if not grupo_repository.obtener_grupo_por_codigo(db, codigo):
            return codigo


def crear_grupo(db: Session, nombre_grupo: str, descripcion: Optional[str], id_usuario: int) -> Grupo:
    codigo_acceso = _generar_codigo_acceso(db)
    grupo = grupo_repository.crear_grupo(db, nombre_grupo, descripcion, codigo_acceso)
    grupo_repository.agregar_integrante(db, id_usuario, grupo.id_grupo, rol="lider")
    return grupo


def eliminar_grupo(db: Session, id_grupo: int) -> None:
    grupo = grupo_repository.obtener_grupo_por_id(db, id_grupo)
    if not grupo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")
    grupo_repository.eliminar_grupo(db, grupo)


def listar_grupos_de_usuario(db: Session, id_usuario: int) -> List[dict]:
    filas = grupo_repository.obtener_grupos_de_usuario(db, id_usuario)
    return [
        {
            "id_grupo": grupo.id_grupo,
            "nombre_grupo": grupo.nombre_grupo,
            "descripcion": grupo.descripcion,
            "codigo_acceso": grupo.codigo_acceso,
            "fecha_creacion": grupo.fecha_creacion,
            "rol": rol,
        }
        for grupo, rol in filas
    ]


def unirse_a_grupo(db: Session, codigo_acceso: str, id_usuario: int) -> Integrante:
    grupo = grupo_repository.obtener_grupo_por_codigo(db, codigo_acceso)
    if not grupo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Código de acceso inválido")

    ya_es_integrante = grupo_repository.obtener_integrante(db, id_usuario, grupo.id_grupo)
    if ya_es_integrante:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya perteneces a este grupo")

    return grupo_repository.agregar_integrante(db, id_usuario, grupo.id_grupo, rol="miembro")


def listar_integrantes_de_grupo(db: Session, id_grupo: int, id_usuario_solicitante: int) -> List[dict]:
    grupo = grupo_repository.obtener_grupo_por_id(db, id_grupo)
    if not grupo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")

    solicitante = grupo_repository.obtener_integrante(db, id_usuario_solicitante, id_grupo)
    if not solicitante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No perteneces a este grupo",
        )

    filas = grupo_repository.obtener_integrantes_de_grupo(db, id_grupo)
    return [
        {
            "id_integrante": integrante.id_integrante,
            "id_usuario": integrante.id_usuario,
            "correo_electronico": usuario.correo_electronico,
            "rol": integrante.rol,
            "fecha_ingreso": integrante.fecha_ingreso,
        }
        for integrante, usuario in filas
    ]


def abandonar_grupo(db: Session, id_grupo: int, id_usuario: int) -> None:
    integrante = grupo_repository.obtener_integrante(db, id_usuario, id_grupo)
    if not integrante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No perteneces a este grupo")

    if integrante.rol == "lider":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El líder no puede abandonar el grupo; transfiere el liderazgo o elimina el grupo",
        )

    grupo_repository.eliminar_integrante(db, integrante)


def expulsar_integrante(db: Session, id_grupo: int, id_usuario_objetivo: int) -> None:
    integrante = grupo_repository.obtener_integrante(db, id_usuario_objetivo, id_grupo)
    if not integrante:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no pertenece a este grupo")

    if integrante.rol == "lider":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes expulsar al líder del grupo",
        )

    grupo_repository.eliminar_integrante(db, integrante)