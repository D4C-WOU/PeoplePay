"""add paid payrun status

Revision ID: c2d8e4f6a1b3
Revises: b7c4f2a1d9e0
Create Date: 2026-09-06

"""

from typing import Sequence, Union

from alembic import op

revision: str = "c2d8e4f6a1b3"
down_revision: Union[str, Sequence[str], None] = "b7c4f2a1d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE payruns
        MODIFY COLUMN status ENUM(
            'DRAFT',
            'PROCESSING',
            'COMPLETED',
            'PAID',
            'CANCELLED'
        ) NOT NULL DEFAULT 'DRAFT'
        """)


def downgrade() -> None:
    op.execute("""
        UPDATE payruns SET status = 'COMPLETED' WHERE status = 'PAID'
        """)
    op.execute("""
        ALTER TABLE payruns
        MODIFY COLUMN status ENUM(
            'DRAFT',
            'PROCESSING',
            'COMPLETED',
            'CANCELLED'
        ) NOT NULL DEFAULT 'DRAFT'
        """)
