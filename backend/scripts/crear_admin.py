"""Crea o promueve un administrador sin credenciales predeterminadas."""

from collections.abc import Mapping
from getpass import getpass
import os
import sys
from typing import Callable

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.perfil import Perfil
from app.models.usuario import Usuario
from app.schemas.contrasena import LONGITUD_MINIMA_CONTRASENA
from app.services.usuario_service import hash_password


_VALIDADOR_CORREO = TypeAdapter(EmailStr)


def _validar_datos(correo: str, contrasena: str) -> tuple[str, str]:
    try:
        correo_validado = str(_VALIDADOR_CORREO.validate_python(correo.strip()))
    except ValidationError:
        raise ValueError("El correo no tiene un formato válido.") from None

    if len(contrasena) < LONGITUD_MINIMA_CONTRASENA or not contrasena.strip():
        raise ValueError(
            f"La contraseña debe tener al menos {LONGITUD_MINIMA_CONTRASENA} caracteres."
        )
    return correo_validado, contrasena


def obtener_credenciales(
    entorno: Mapping[str, str] | None = None,
    *,
    leer: Callable[[str], str] = input,
    leer_secreto: Callable[[str], str] = getpass,
) -> tuple[str, str]:
    entorno = os.environ if entorno is None else entorno
    correo = entorno.get("ACADEX_ADMIN_EMAIL", "").strip()
    contrasena = entorno.get("ACADEX_ADMIN_PASSWORD", "")

    if correo or contrasena:
        if not correo or not contrasena:
            raise ValueError(
                "Define ACADEX_ADMIN_EMAIL y ACADEX_ADMIN_PASSWORD juntas."
            )
    else:
        correo = leer("Correo del administrador: ").strip()
        contrasena = leer_secreto("Contraseña nueva: ")
        confirmacion = leer_secreto("Confirma la contraseña: ")
        if contrasena != confirmacion:
            raise ValueError("Las contraseñas no coinciden.")

    return _validar_datos(correo, contrasena)


def crear_o_promover_administrador(
    db: Session,
    correo: str,
    contrasena: str,
) -> str:
    correo, contrasena = _validar_datos(correo, contrasena)
    usuario = (
        db.query(Usuario)
        .filter(Usuario.correo_electronico == correo)
        .first()
    )
    era_admin = bool(usuario and usuario.es_admin)
    hash_nuevo = hash_password(contrasena)

    if usuario is None:
        usuario = Usuario(
            correo_electronico=correo,
            contrasena=hash_nuevo,
            es_admin=True,
        )
        db.add(usuario)
        db.flush()
        estado = "creado"
    else:
        usuario.contrasena = hash_nuevo
        usuario.es_admin = True
        estado = "actualizado" if era_admin else "promovido"

    perfil = (
        db.query(Perfil)
        .filter(Perfil.id_usuario == usuario.id_usuario)
        .first()
    )
    if perfil is None:
        db.add(
            Perfil(
                id_usuario=usuario.id_usuario,
                nombre_usuario=correo.split("@", 1)[0][:50],
            )
        )

    try:
        db.commit()
        db.refresh(usuario)
    except Exception:
        db.rollback()
        raise
    return estado


def main() -> int:
    try:
        correo, contrasena = obtener_credenciales()
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    try:
        with Session(engine) as db:
            estado = crear_o_promover_administrador(db, correo, contrasena)
    except Exception:
        print("No se pudo guardar el usuario administrador.", file=sys.stderr)
        return 1

    print(f"Administrador {estado} correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
