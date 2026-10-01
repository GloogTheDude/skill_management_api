"""add employee declared skill acquisition

Revision ID: 8d3e4f5a6b7c
Revises: c3a8f1e2b4d6
"""

from alembic import op
import sqlalchemy as sa


revision = "8d3e4f5a6b7c"
down_revision = "c3a8f1e2b4d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee_declared_skill",
        sa.Column("id_employee_declared_skill", sa.Integer(), primary_key=True),
        sa.Column("id_employee", sa.Integer(), nullable=False),
        sa.Column("id_skill", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("acquired_at", sa.Date(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.ForeignKeyConstraint(["id_employee"], ["employee.id_employee"]),
        sa.ForeignKeyConstraint(["id_skill"], ["skill.id_skill"]),
        sa.UniqueConstraint("id_employee", "id_skill", name="uq_employee_declared_skill"),
        sa.CheckConstraint("level BETWEEN 1 AND 5", name="ck_employee_declared_skill_level"),
    )


def downgrade() -> None:
    op.drop_table("employee_declared_skill")
