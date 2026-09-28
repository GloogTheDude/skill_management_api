"""add active employee mail unique index

Revision ID: c4f1a8b2d9e0
Revises: a911db9d2ce2
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4f1a8b2d9e0"
down_revision: Union[str, Sequence[str], None] = "a911db9d2ce2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_employee_mail_active",
        "employee",
        ["mail"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )


def downgrade() -> None:
    op.drop_index("uq_employee_mail_active", table_name="employee")
