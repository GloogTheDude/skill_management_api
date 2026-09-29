"""add participation documents

Revision ID: 4e5f6a7b8c9d
Revises: e7a2c5f91b34
"""

from alembic import op
import sqlalchemy as sa


revision = "4e5f6a7b8c9d"
down_revision = "e7a2c5f91b34"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "participation_document",
        sa.Column("id_participation_document", sa.Integer(), primary_key=True),
        sa.Column("id_employee", sa.Integer(), nullable=False),
        sa.Column("id_training", sa.Integer(), nullable=False),
        sa.Column("document_type", sa.String(length=40), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id_uploaded_by", sa.Integer(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_employee", "id_training"],
            ["participation.id_employee", "participation.id_training"],
        ),
        sa.ForeignKeyConstraint(["id_uploaded_by"], ["employee.id_employee"]),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(
        "ix_participation_document_participation",
        "participation_document",
        ["id_employee", "id_training", "is_deleted"],
    )


def downgrade() -> None:
    op.drop_index("ix_participation_document_participation", table_name="participation_document")
    op.drop_table("participation_document")
