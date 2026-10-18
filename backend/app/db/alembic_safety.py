"""Protecciones para adoptar una base existente con Alembic."""

from sqlalchemy import inspect, text


GUIA_ADOPCION = "docs/DESPLIEGUE_ALEMBIC.md"


def obtener_comando_alembic(config) -> str | None:
    """Devuelve el nombre del comando CLI actual, si Alembic lo expone."""
    opciones = getattr(config, "cmd_opts", None)
    comando = getattr(opciones, "cmd", None)
    if isinstance(comando, str):
        return comando
    if isinstance(comando, tuple) and comando:
        comando = comando[0]
    return getattr(comando, "__name__", None)


def validar_historial_esquema(
    connection,
    *,
    tablas_esperadas: set[str],
    comando: str | None,
    permitir_adopcion: bool,
) -> None:
    """Rechaza esquemas existentes sin historial, salvo adopción explícita."""
    inspector = inspect(connection)
    tablas_publicas = set(inspector.get_table_names(schema="public"))
    tablas_acadex = tablas_publicas & tablas_esperadas
    tiene_tabla_version = inspector.has_table("alembic_version", schema="public")

    if not tiene_tabla_version:
        if not tablas_acadex:
            if comando == "stamp":
                raise RuntimeError(
                    "No se permite stamp en una base vacía. Para crear el esquema, "
                    "use upgrade; stamp se reserva para adoptar una base existente."
                )
            return

        if comando == "stamp" and permitir_adopcion:
            faltantes = sorted(tablas_esperadas - tablas_publicas)
            if faltantes:
                lista = ", ".join(faltantes)
                raise RuntimeError(
                    "No se puede adoptar la base: faltan tablas Acadex esperadas "
                    f"en public: {lista}. Compare el esquema y revise "
                    f"{GUIA_ADOPCION}."
                )
            return

        raise RuntimeError(
            "Alembic se detuvo: public ya contiene tablas de Acadex pero no "
            "existe public.alembic_version. Para adoptar una base existente, "
            "compare y reconcilie el esquema según "
            f"{GUIA_ADOPCION}; después use ALEMBIC_ALLOW_ADOPT_EXISTING=1 "
            "solo para el comando stamp. No ejecute upgrade a ciegas."
        )

    revisiones = connection.execute(
        text("SELECT version_num FROM public.alembic_version")
    ).scalars().all()
    if not revisiones and tablas_acadex:
        raise RuntimeError(
            "Alembic se detuvo: public.alembic_version está vacío y ya hay tablas "
            "de Acadex. Compare y reconcilie esa base antes de continuar."
        )
