"""Add user identity link to department administrators.

Revision ID: b71f0c1d2026
Revises: d084ff6d14cb
"""

from alembic import op
import sqlalchemy as sa


revision = "b71f0c1d2026"
down_revision = "d084ff6d14cb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "department_administrators",
        sa.Column("user_id", sa.String(36), nullable=True),
    )

    op.create_foreign_key(
        "fk_department_administrators_user_id_users",
        "department_administrators",
        "users",
        ["user_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_unique_constraint(
        "uq_department_administrators_user_id",
        "department_administrators",
        ["user_id"],
    )


def downgrade():
    op.drop_constraint(
        "uq_department_administrators_user_id",
        "department_administrators",
        type_="unique",
    )

    op.drop_constraint(
        "fk_department_administrators_user_id_users",
        "department_administrators",
        type_="foreignkey",
    )

    op.drop_column(
        "department_administrators",
        "user_id",
    )