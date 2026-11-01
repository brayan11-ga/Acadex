"""Cronómetro: columnas de aviso en sesiones y límite en segundos en perfiles."""

from alembic import op


revision = "20261031_01"
down_revision = "20261018_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE public.sesiones_cronometro "
        "ADD COLUMN IF NOT EXISTS fecha_aviso TIMESTAMP, "
        "ADD COLUMN IF NOT EXISTS fecha_confirmacion TIMESTAMP"
    )
    # Minutos -> segundos una sola vez. Si el default ya es 1800, la base ya se
    # convirtió (por ejemplo, con el script manual) y no se multiplica de nuevo.
    op.execute(
        """
        DO $$
        BEGIN
            IF COALESCE((
                SELECT column_default FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'perfiles'
                  AND column_name = 'limite_cronometro'
            ), '') <> '1800' THEN
                UPDATE public.perfiles
                SET limite_cronometro = limite_cronometro * 60
                WHERE limite_cronometro IS NOT NULL;
            END IF;
        END
        $$
        """
    )
    op.execute(
        "UPDATE public.perfiles SET limite_cronometro = 1800 "
        "WHERE limite_cronometro IS NULL"
    )
    op.execute("ALTER TABLE public.perfiles ALTER COLUMN limite_cronometro SET DEFAULT 1800")
    op.execute("ALTER TABLE public.perfiles ALTER COLUMN limite_cronometro SET NOT NULL")


def downgrade() -> None:
    # Vuelve a minutos (división entera: se pierde la precisión de segundos).
    op.execute("ALTER TABLE public.perfiles ALTER COLUMN limite_cronometro DROP NOT NULL")
    op.execute("ALTER TABLE public.perfiles ALTER COLUMN limite_cronometro DROP DEFAULT")
    op.execute(
        "UPDATE public.perfiles "
        "SET limite_cronometro = GREATEST(limite_cronometro / 60, 1) "
        "WHERE limite_cronometro IS NOT NULL"
    )
    op.execute(
        "ALTER TABLE public.sesiones_cronometro "
        "DROP COLUMN IF EXISTS fecha_confirmacion, "
        "DROP COLUMN IF EXISTS fecha_aviso"
    )