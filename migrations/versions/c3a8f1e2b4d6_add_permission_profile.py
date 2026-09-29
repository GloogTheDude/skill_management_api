"""decouple authorization from access level rank"""

from alembic import op
import sqlalchemy as sa


revision = "c3a8f1e2b4d6"
down_revision = "7f1c2d9e4a10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "access_level",
        sa.Column("permission_profile", sa.String(length=20), nullable=True),
    )
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM access_level WHERE level NOT IN (1, 2, 3)) THEN
                RAISE EXCEPTION 'Cannot backfill permission_profile: unexpected access level rank';
            END IF;
        END $$;
    """)
    op.execute("""
        UPDATE access_level
        SET permission_profile = CASE level
            WHEN 1 THEN 'EMPLOYEE'
            WHEN 2 THEN 'MANAGER'
            WHEN 3 THEN 'HR'
        END
    """)
    op.alter_column(
        "access_level",
        "permission_profile",
        existing_type=sa.String(length=20),
        nullable=False,
    )
    op.create_check_constraint(
        "ck_access_level_permission_profile",
        "access_level",
        "permission_profile IN ('EMPLOYEE', 'MANAGER', 'HR')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_access_level_permission_profile", "access_level", type_="check")
    op.drop_column("access_level", "permission_profile")
