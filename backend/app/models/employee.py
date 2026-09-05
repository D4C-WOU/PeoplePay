import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"


class EmployeeType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERN = "INTERN"


class Employee(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "employees"

    __table_args__ = (
        Index("ix_employees_manager_id", "manager_id"),
        Index("ix_employees_employee_type", "employee_type"),
    )

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
    )
    department_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    manager_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    employee_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    employee_type: Mapped[EmployeeType] = mapped_column(
        Enum(EmployeeType), default=EmployeeType.FULL_TIME, nullable=False
    )
    status: Mapped[EmployeeStatus] = mapped_column(
        Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False
    )
    bank_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    bank_account_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bank_ifsc: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact_name: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )
    emergency_contact_phone: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )

    user: Mapped["User | None"] = relationship(back_populates="employee")
    department: Mapped["Department | None"] = relationship(back_populates="employees")
    manager: Mapped["Employee | None"] = relationship(
        "Employee", remote_side="Employee.id", back_populates="direct_reports"
    )
    direct_reports: Mapped[list["Employee"]] = relationship(
        "Employee", back_populates="manager"
    )
    contracts: Mapped[list["Contract"]] = relationship(back_populates="employee")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="employee"
    )
    time_off_allocations: Mapped[list["TimeOffAllocation"]] = relationship(
        back_populates="employee"
    )
    time_off_requests: Mapped[list["TimeOffRequest"]] = relationship(
        back_populates="employee"
    )
    payslips: Mapped[list["Payslip"]] = relationship(back_populates="employee")
