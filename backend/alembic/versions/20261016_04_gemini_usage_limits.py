"""Crea contadores diarios para los límites de análisis de IA."""

from alembic import op
import sqlalchemy as sa


revision = "20261016_04"
down_revision = "20261016_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "uso_analisis_ia",
        sa.Column("fecha_utc", sa.Date(), nullable=False),
        sa.Column("alcance", sa.String(length=10), nullable=False),
        sa.Column("identificador_alcance", sa.String(length=64), nullable=False),
        sa.Column(
            "cantidad", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.CheckConstraint("cantidad >= 0", name="ck_uso_analisis_ia_cantidad"),
        sa.CheckConstraint(
            "(alcance = 'usuario' AND identificador_alcance <> '') "
            "OR (alcance = 'global' AND identificador_alcance = 'global')",
            name="ck_uso_analisis_ia_alcance",
        ),
        sa.PrimaryKeyConstraint(
            "fecha_utc", "alcance", "identificador_alcance", name="pk_uso_analisis_ia"
        ),
        schema="public",
    )


def downgrade() -> None:
    rows_exist = op.get_bind().execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM public.uso_analisis_ia LIMIT 1)")
    ).scalar_one()
    if rows_exist:
        raise RuntimeError(
            "No se puede revertir: uso_analisis_ia conserva contadores. "
            "Exporte y revise esos datos antes de una reversión manual."
        )
    op.drop_table("uso_analisis_ia", schema="public")
