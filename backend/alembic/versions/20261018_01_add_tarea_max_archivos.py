"""Añade el límite de archivos por tarea (tareas.max_archivos)."""

from alembic import op


revision = "20261018_01"
down_revision = "20261016_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Repetible: una base existente recibe max_archivos con el tope del sistema (10).
    op.execute(
        "ALTER TABLE public.tareas "
        "ADD COLUMN IF NOT EXISTS max_archivos INTEGER NOT NULL DEFAULT 10"
    )
    # ADD CONSTRAINT no admite IF NOT EXISTS: se busca el constraint antes de crearlo.
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'chk_max_archivos'
                  AND conrelid = 'public.tareas'::regclass
            ) THEN
                ALTER TABLE public.tareas
                    ADD CONSTRAINT chk_max_archivos CHECK (max_archivos >= 1);
            END IF;
        END
        $$
        """
    )
    op.execute(
        "COMMENT ON COLUMN public.tareas.max_archivos IS "
        "'Máximo de archivos permitidos en la tarea (1..10). Tope fijo del sistema: 10.'"
    )


def downgrade() -> None:
    # Retirar la columna descarta los límites que el líder configuró; no hay datos
    # derivables que restaurar. Se elimina primero el constraint y luego la columna.
    op.execute("ALTER TABLE public.tareas DROP CONSTRAINT IF EXISTS chk_max_archivos")
    op.execute("ALTER TABLE public.tareas DROP COLUMN IF EXISTS max_archivos")
