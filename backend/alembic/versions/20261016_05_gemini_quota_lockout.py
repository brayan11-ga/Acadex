"""Crea el bloqueo persistente por agotamiento de cuota de Gemini."""

from alembic import op
import sqlalchemy as sa


revision = "20261016_05"
down_revision = "20261016_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bloqueo_cuota_gemini",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("bloqueado_hasta", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("id = 'proyecto'", name="ck_bloqueo_cuota_gemini_id"),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )


def downgrade() -> None:
    rows_exist = op.get_bind().execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM public.bloqueo_cuota_gemini LIMIT 1)"
        )
    ).scalar_one()
    if rows_exist:
        raise RuntimeError(
            "No se puede revertir: bloqueo_cuota_gemini conserva el estado "
            "de cuota agotada. Revise el bloqueo antes de una reversión manual."
        )
    op.drop_table("bloqueo_cuota_gemini", schema="public")
