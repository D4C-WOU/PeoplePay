"""complete PeoplePay payroll requirements

Revision ID: 8a2f1c4d7e90
Revises: 4094dbc99e33
Create Date: 2026-09-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "8a2f1c4d7e90"
down_revision: Union[str, Sequence[str], None] = "4094dbc99e33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Employees
    # ---------------------------------------------------------

    op.add_column(
        "employees",
        sa.Column(
            "manager_id",
            sa.String(length=36),
            nullable=True,
        ),
    )

    op.add_column(
        "employees",
        sa.Column(
            "employee_type",
            sa.Enum(
                "FULL_TIME",
                "PART_TIME",
                "CONTRACT",
                "INTERN",
                name="employee_type",
            ),
            nullable=True,
        ),
    )

    op.add_column(
        "employees",
        sa.Column(
            "bank_name",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "employees",
        sa.Column(
            "bank_account_number",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "employees",
        sa.Column(
            "bank_ifsc",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_employees_manager_id",
        "employees",
        ["manager_id"],
    )

    op.create_index(
        "ix_employees_employee_type",
        "employees",
        ["employee_type"],
    )

    op.create_foreign_key(
        "fk_employees_manager_id",
        "employees",
        "employees",
        ["manager_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ---------------------------------------------------------
    # Payruns
    # ---------------------------------------------------------

    op.add_column(
        "payruns",
        sa.Column(
            "salary_structure_id",
            sa.String(length=36),
            nullable=True,
        ),
    )

    op.add_column(
        "payruns",
        sa.Column(
            "selected_employee_ids",
            sa.JSON(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_payruns_salary_structure_id",
        "payruns",
        "salary_structures",
        ["salary_structure_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ---------------------------------------------------------
    # Work schedule days
    # ---------------------------------------------------------

    op.create_table(
        "work_schedule_days",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "work_schedule_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "day_of_week",
            sa.Enum(
                "MONDAY",
                "TUESDAY",
                "WEDNESDAY",
                "THURSDAY",
                "FRIDAY",
                "SATURDAY",
                "SUNDAY",
                name="day_of_week",
            ),
            nullable=False,
        ),
        sa.Column(
            "start_time",
            sa.Time(),
            nullable=True,
        ),
        sa.Column(
            "end_time",
            sa.Time(),
            nullable=True,
        ),
        sa.Column(
            "break_minutes",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.ForeignKeyConstraint(
            ["work_schedule_id"],
            ["work_schedules.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "work_schedule_id",
            "day_of_week",
            name="uq_work_schedule_day",
        ),
    )

    op.create_index(
        "ix_work_schedule_days_work_schedule_id",
        "work_schedule_days",
        ["work_schedule_id"],
    )


def downgrade() -> None:
    # Work schedule days
    op.drop_index(
        "ix_work_schedule_days_work_schedule_id",
        table_name="work_schedule_days",
    )

    op.drop_table("work_schedule_days")

    # Payruns
    op.drop_constraint(
        "fk_payruns_salary_structure_id",
        "payruns",
        type_="foreignkey",
    )

    op.drop_column("payruns", "selected_employee_ids")
    op.drop_column("payruns", "salary_structure_id")

    # Employees
    op.drop_constraint(
        "fk_employees_manager_id",
        "employees",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_employees_employee_type",
        table_name="employees",
    )

    op.drop_index(
        "ix_employees_manager_id",
        table_name="employees",
    )

    op.drop_column("employees", "bank_ifsc")
    op.drop_column("employees", "bank_account_number")
    op.drop_column("employees", "bank_name")
    op.drop_column("employees", "employee_type")
    op.drop_column("employees", "manager_id")
