"""harden skill validation lifecycle

Revision ID: 7f1c2d9e4a10
Revises: 4e5f6a7b8c9d
"""

from alembic import op
import sqlalchemy as sa


revision = "7f1c2d9e4a10"
down_revision = "4e5f6a7b8c9d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("skill_validation", sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("skill_validation", sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("skill_validation", sa.Column("justification", sa.String(length=1000), nullable=True))

    op.execute("""
        UPDATE skill_validation
        SET validated_at = COALESCE(date_::timestamp AT TIME ZONE 'UTC', CURRENT_TIMESTAMP)
        WHERE validated_at IS NULL
    """)
    op.execute("""
        WITH ranked AS (
            SELECT id_skill_validation,
                   ROW_NUMBER() OVER (
                       PARTITION BY id_employee, id_skill
                       ORDER BY validated_at DESC, id_skill_validation DESC
                   ) AS position
            FROM skill_validation
            WHERE is_deleted = false AND superseded_at IS NULL
        )
        UPDATE skill_validation AS target
        SET superseded_at = target.validated_at
        FROM ranked
        WHERE target.id_skill_validation = ranked.id_skill_validation
          AND ranked.position > 1
    """)
    op.create_index(
        "uq_skill_validation_current_employee_skill",
        "skill_validation",
        ["id_employee", "id_skill"],
        unique=True,
        postgresql_where=sa.text("superseded_at IS NULL AND is_deleted = false"),
        sqlite_where=sa.text("superseded_at IS NULL AND is_deleted = 0"),
    )


def downgrade() -> None:
    op.drop_index("uq_skill_validation_current_employee_skill", table_name="skill_validation")
    op.drop_column("skill_validation", "justification")
    op.drop_column("skill_validation", "superseded_at")
    op.drop_column("skill_validation", "validated_at")
