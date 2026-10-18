"""Agrega el estado de bloqueo, límites compartidos y unicidad de cronómetro."""

from alembic import op
import sqlalchemy as sa


revision = "20261016_06"
down_revision = "20261016_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "intentos_fallidos",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        schema="public",
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "bloqueado", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        schema="public",
    )
    op.add_column(
        "usuarios",
        sa.Column("bloqueado_hasta", sa.DateTime(), nullable=True),
        schema="public",
    )
    op.create_table(
        "limites_solicitud",
        sa.Column("alcance", sa.String(length=40), nullable=False),
        sa.Column("clave_hash", sa.String(length=64), nullable=False),
        sa.Column("inicio_ventana", sa.DateTime(), nullable=False),
        sa.Column(
            "cantidad", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.CheckConstraint("cantidad >= 0", name="ck_limites_solicitud_cantidad"),
        sa.PrimaryKeyConstraint(
            "alcance", "clave_hash", name="pk_limites_solicitud"
        ),
        schema="public",
    )

    duplicadas = op.get_bind().execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM public.sesiones_cronometro "
            "WHERE fecha_fin IS NULL GROUP BY id_tarea HAVING COUNT(*) > 1)"
        )
    ).scalar_one()
    if duplicadas:
        raise RuntimeError(
            "Hay tareas con varias sesiones activas. Revise esas filas antes "
            "de crear uq_sesiones_tarea_activa."
        )
    op.create_index(
        "uq_sesiones_tarea_activa",
        "sesiones_cronometro",
        ["id_tarea"],
        unique=True,
        schema="public",
        postgresql_where=sa.text("fecha_fin IS NULL"),
    )


def downgrade() -> None:
    raise RuntimeError(
        "Esta revisión no tiene downgrade automático: retirar límites o estado "
        "de bloqueo puede perder datos y quitar uq_sesiones_tarea_activa debilita "
        "una protección de integridad. Requiere una reversión manual coordinada "
        "con una copia de seguridad y una versión compatible de la aplicación."
    )
