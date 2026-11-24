"""Aplica Alembic y verifica el historial antes y después de migrar."""

import argparse
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.util import CommandError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Permite inicializar una base nueva en desarrollo o pruebas.",
    )
    args = parser.parse_args()

    try:
        from app.config.settings import settings

        if args.allow_empty and settings.app_env == "production":
            raise RuntimeError("--allow-empty está reservado para desarrollo y pruebas.")

        config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        head = ScriptDirectory.from_config(config).get_current_head()
        if head is None:
            raise RuntimeError("El código debe contener una revisión head de Alembic.")

        config.attributes["revision_predeploy"] = head
        config.attributes["permitir_base_vacia"] = args.allow_empty
        command.upgrade(config, head)
    except ValidationError as error:
        campos = ", ".join(
            sorted({str(item["loc"][0]) for item in error.errors(include_input=False)})
        )
        print(f"Configuración inválida para migrar. Revisa: {campos}", file=sys.stderr)
        return 1
    except SQLAlchemyError as error:
        sqlstate = getattr(getattr(error, "orig", None), "pgcode", None)
        detalle = f"SQLSTATE {sqlstate}" if sqlstate else type(error).__name__
        print(f"Falló la conexión o la operación de PostgreSQL ({detalle}).", file=sys.stderr)
        return 1
    except (CommandError, RuntimeError) as error:
        print(f"Pre-Deploy de Alembic: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
