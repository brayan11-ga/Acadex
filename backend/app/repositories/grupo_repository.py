# backend/app/repositories/grupo_repository.py
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.grupo import Grupo
from app.models.integrante import Integrante
from app.models.usuario import Usuario


def obtener_grupo_por_id(db: Session, id_grupo: int) -> Optional[Grupo]:
    return db.query(Grupo).filter(Grupo.id_grupo == id_grupo).first()


def obtener_grupo_por_codigo(db: Session, codigo_acceso: str) -> Optional[Grupo]:
    return db.query(Grupo).filter(Grupo.codigo_acceso == codigo_acceso).first()


def obtener_grupos_de_usuario(db: Session, id_usuario: int) -> List[Tuple[Grupo, str]]:
    return (
        db.query(Grupo, Integrante.rol)
        .join(Integrante, Integrante.id_grupo == Grupo.id_grupo)
        .filter(Integrante.id_usuario == id_usuario)
        .all()
    )


def crear_grupo(db: Session, nombre_grupo: str, descripcion: Optional[str], codigo_acceso: str) -> Grupo:
    grupo = Grupo(
        nombre_grupo=nombre_grupo,
        descripcion=descripcion,
        codigo_acceso=codigo_acceso,
    )
    db.add(grupo)
    db.commit()
    db.refresh(grupo)
    return grupo


def eliminar_grupo(db: Session, grupo: Grupo) -> None:
    db.delete(grupo)
    db.commit()


def obtener_integrante(db: Session, id_usuario: int, id_grupo: int) -> Optional[Integrante]:
    return (
        db.query(Integrante)
        .filter(Integrante.id_usuario == id_usuario, Integrante.id_grupo == id_grupo)
        .first()
    )


def agregar_integrante(db: Session, id_usuario: int, id_grupo: int, rol: str) -> Integrante:
    integrante = Integrante(rol=rol, id_usuario=id_usuario, id_grupo=id_grupo)
    db.add(integrante)
    db.commit()
    db.refresh(integrante)
    return integrante


def eliminar_integrante(db: Session, integrante: Integrante) -> None:
    db.delete(integrante)
    db.commit()


def obtener_integrantes_de_grupo(db: Session, id_grupo: int) -> List[Tuple[Integrante, Usuario]]:
    return (
        db.query(Integrante, Usuario)
        .join(Usuario, Usuario.id_usuario == Integrante.id_usuario)
        .filter(Integrante.id_grupo == id_grupo)
        .all()
    )