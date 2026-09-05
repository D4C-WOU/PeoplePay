"""add salary rule basis

Revision ID: b7c4f2a1d9e0
Revises: 8a2f1c4d7e90
Create Date: 2026-09-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b7c4f2a1d9e0"
down_revision: Union[str, Sequence[str], None] = "8a2f1c4d7e90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "salary_rules",
        sa.Column("based_on", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("salary_rules", "based_on")
