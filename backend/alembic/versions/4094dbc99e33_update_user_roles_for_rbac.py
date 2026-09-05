"""update user roles for rbac

Revision ID: 4094dbc99e33
Revises: 970747534695
Create Date: 2026-09-05 17:06:17.356270

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4094dbc99e33"
down_revision: Union[str, Sequence[str], None] = "970747534695"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First convert existing HR users to the new role name.
    op.execute("""
        UPDATE users
        SET role = 'HR_MANAGER'
        WHERE role = 'HR'
        """)

    # Update the MySQL ENUM to contain all PeoplePay360 roles.
    op.execute("""
        ALTER TABLE users
        MODIFY COLUMN role ENUM(
            'ADMIN',
            'HR_MANAGER',
            'MANAGER',
            'EMPLOYEE',
            'PAYROLL_MANAGER',
            'PAYROLL_USER'
        ) NOT NULL DEFAULT 'EMPLOYEE'
        """)


def downgrade() -> None:
    # Convert the new HR role back before removing it from the ENUM.
    op.execute("""
        UPDATE users
        SET role = 'HR'
        WHERE role = 'HR_MANAGER'
        """)

    # Restore the original role ENUM.
    op.execute("""
        ALTER TABLE users
        MODIFY COLUMN role ENUM(
            'ADMIN',
            'HR',
            'MANAGER',
            'EMPLOYEE'
        ) NOT NULL DEFAULT 'EMPLOYEE'
        """)
