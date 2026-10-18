"""Añade la autoría opcional de los archivos subidos."""

from alembic import op
import sqlalchemy as sa


revision = "20261016_02"
down_revision = "20261016_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "archivos",
        sa.Column("id_usuario_subida", sa.Integer(), nullable=True),
        schema="public",
    )
    op.create_foreign_key(
        "fk_archivos_usuario_subida",
        "archivos",
        "usuarios",
        ["id_usuario_subida"],
        ["id_usuario"],
        source_schema="public",
        referent_schema="public",
        ondelete="SET NULL",
    )
    op.execute(
        "COMMENT ON COLUMN public.archivos.id_usuario_subida IS "
        "'Usuario autenticado que subió el adjunto; NULL identifica registros "
        "históricos sin autor verificable.'"
    )


def downgrade() -> None:
    authors_exist = op.get_bind().execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM public.archivos "
            "WHERE id_usuario_subida IS NOT NULL)"
        )
    ).scalar_one()
    if authors_exist:
        raise RuntimeError(
            "No se puede revertir: se perderían autorías de archivos. "
            "Exporte y revise esos datos antes de una operación manual."
        )
    op.drop_constraint(
        "fk_archivos_usuario_subida", "archivos", schema="public", type_="foreignkey"
    )
    op.drop_column("archivos", "id_usuario_subida", schema="public")
