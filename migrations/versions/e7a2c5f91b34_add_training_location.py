"""add location to training

Revision ID: e7a2c5f91b34
Revises: c4f1a8b2d9e0
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7a2c5f91b34"
down_revision: Union[str, Sequence[str], None] = "c4f1a8b2d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "training",
        sa.Column("location", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("training", "location")
