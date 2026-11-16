"""Añade el vencimiento del código de acceso de los grupos."""

from alembic import op


revision = "20261115_01"
down_revision = "20261110_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NULL = código vencido (no se rellenan los grupos existentes a propósito).
    # UTC sin zona horaria, igual que usuarios.bloqueado_hasta.
    op.execute(
        "ALTER TABLE public.grupos "
        "ADD COLUMN IF NOT EXISTS fecha_expiracion_codigo TIMESTAMP WITHOUT TIME ZONE"
    )
    op.execute(
        "COMMENT ON COLUMN public.grupos.fecha_expiracion_codigo IS "
        "'Vencimiento UTC del código de acceso. NULL = vencido.'"
    )


def downgrade() -> None:
    # Eliminar la columna descarta las fechas de vencimiento guardadas; los
    # códigos quedan sin vigencia y habrá que regenerarlos tras volver atrás.
    op.execute(
        "ALTER TABLE public.grupos DROP COLUMN IF EXISTS fecha_expiracion_codigo"
    )
