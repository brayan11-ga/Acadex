"""Cambia el cronómetro activo a uno por (tarea, usuario)."""

from alembic import op


revision = "20261110_01"
down_revision = "20261018_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # La regla nueva es menos estricta: cada asignado puede tener su propia
    # sesión abierta en la misma tarea. Se reemplaza el índice parcial único.
    op.execute("DROP INDEX IF EXISTS public.uq_sesiones_tarea_activa")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_sesiones_tarea_activa "
        "ON public.sesiones_cronometro (id_tarea, id_usuario) "
        "WHERE fecha_fin IS NULL"
    )


def downgrade() -> None:
    # Puede fallar si ya hay dos usuarios con sesión abierta en la misma tarea:
    # esas filas violarían el índice viejo (uno por tarea). Revísalas antes.
    op.execute("DROP INDEX IF EXISTS public.uq_sesiones_tarea_activa")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_sesiones_tarea_activa "
        "ON public.sesiones_cronometro (id_tarea) "
        "WHERE fecha_fin IS NULL"
    )
