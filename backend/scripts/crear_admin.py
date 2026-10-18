"""Crea o promueve un administrador sin credenciales predeterminadas."""

import argparse
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


def _validar_correo(correo: str) -> str:
    try:
        return str(_VALIDADOR_CORREO.validate_python(correo.strip()))
    except ValidationError:
        raise ValueError("El correo no tiene un formato válido.") from None


def _validar_contrasena(contrasena: str) -> str:
    if len(contrasena) < LONGITUD_MINIMA_CONTRASENA or not contrasena.strip():
        raise ValueError(
            f"La contraseña debe tener al menos {LONGITUD_MINIMA_CONTRASENA} caracteres."
        )
    return contrasena


def obtener_correo(
    entorno: Mapping[str, str] | None = None,
    *,
    leer: Callable[[str], str] = input,
) -> str:
    entorno = os.environ if entorno is None else entorno
    correo = entorno.get("ACADEX_ADMIN_EMAIL", "").strip()
    if not correo:
        correo = leer("Correo del administrador: ").strip()
    return _validar_correo(correo)


def obtener_contrasena(
    entorno: Mapping[str, str] | None = None,
    *,
    leer_secreto: Callable[[str], str] = getpass,
) -> str:
    entorno = os.environ if entorno is None else entorno
    contrasena = entorno.get("ACADEX_ADMIN_PASSWORD", "")
    confirmacion = entorno.get("ACADEX_ADMIN_PASSWORD_CONFIRM", "")

    if contrasena or confirmacion:
        if not contrasena or not confirmacion:
            raise ValueError(
                "Define ACADEX_ADMIN_PASSWORD y ACADEX_ADMIN_PASSWORD_CONFIRM juntas."
            )
    else:
        contrasena = leer_secreto("Contraseña nueva: ")
        confirmacion = leer_secreto("Confirma la contraseña: ")

    if contrasena != confirmacion:
        raise ValueError("Las contraseñas no coinciden.")
    return _validar_contrasena(contrasena)


def crear_o_promover_administrador(
    db: Session,
    correo: str,
    contrasena: str | None = None,
    *,
    reset_password: bool = False,
) -> str:
    correo = _validar_correo(correo)
    usuario = (
        db.query(Usuario)
        .filter(Usuario.correo_electronico == correo)
        .first()
    )

    if usuario is None:
        if reset_password:
            raise ValueError("No existe un usuario al cual restablecer la contraseña.")
        if contrasena is None:
            raise ValueError("Se necesita una contraseña para crear el administrador.")
        contrasena = _validar_contrasena(contrasena)
        usuario = Usuario(
            correo_electronico=correo,
            contrasena=hash_password(contrasena),
            es_admin=True,
        )
        db.add(usuario)
        db.flush()
        estado = "creado"
    else:
        era_admin = bool(usuario.es_admin)
        if reset_password:
            if contrasena is None:
                raise ValueError("Se necesita una contraseña confirmada para restablecerla.")
            usuario.contrasena = hash_password(_validar_contrasena(contrasena))
        elif contrasena is not None:
            raise ValueError("Usa --reset-password para cambiar una contraseña existente.")

        usuario.es_admin = True
        estado = "actualizado" if era_admin and reset_password else (
            "ya administrador" if era_admin else "promovido"
        )

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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Crea o promueve un administrador Acadex.")
    parser.add_argument(
        "--reset-password",
        action="store_true",
        help="cambia la contraseña de una cuenta existente tras confirmarla",
    )
    argumentos = parser.parse_args(argv)

    try:
        correo = obtener_correo()
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    try:
        with Session(engine) as db:
            existe = (
                db.query(Usuario)
                .filter(Usuario.correo_electronico == correo)
                .first()
                is not None
            )
            if argumentos.reset_password and not existe:
                raise ValueError("No existe un usuario al cual restablecer la contraseña.")

            requiere_contrasena = not existe or argumentos.reset_password
            contrasena = obtener_contrasena() if requiere_contrasena else None
            estado = crear_o_promover_administrador(
                db,
                correo,
                contrasena,
                reset_password=argumentos.reset_password,
            )
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    except Exception:
        print("No se pudo guardar el usuario administrador.", file=sys.stderr)
        return 1

    print(f"Administrador {estado} correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
