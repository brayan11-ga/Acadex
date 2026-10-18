"""Crea la evidencia versionada de consentimientos de registro."""

from alembic import op
import sqlalchemy as sa


revision = "20261016_03"
down_revision = "20261016_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consentimientos_usuario",
        sa.Column("id_consentimiento", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("tipo_consentimiento", sa.String(length=40), nullable=False),
        sa.Column("version_politica", sa.String(length=30), nullable=False),
        sa.Column(
            "fecha_aceptacion",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "tipo_consentimiento IN ('tratamiento_datos', 'aviso_almacenamiento')",
            name="chk_consentimientos_usuario_tipo",
        ),
        sa.ForeignKeyConstraint(
            ["id_usuario"],
            ["public.usuarios.id_usuario"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id_consentimiento"),
        sa.UniqueConstraint(
            "id_usuario",
            "tipo_consentimiento",
            "version_politica",
            name="uq_consentimientos_usuario_version",
        ),
        schema="public",
    )
    op.execute(
        "COMMENT ON TABLE public.consentimientos_usuario IS "
        "'Evidencia versionada de autorización de tratamiento de datos y "
        "lectura del aviso de almacenamiento local.'"
    )


def downgrade() -> None:
    evidence_exists = op.get_bind().execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM public.consentimientos_usuario LIMIT 1)"
        )
    ).scalar_one()
    if evidence_exists:
        raise RuntimeError(
            "No se puede revertir: consentimientos_usuario conserva evidencia. "
            "Exporte y gestione esos registros antes de una reversión manual."
        )
    op.drop_table("consentimientos_usuario", schema="public")
