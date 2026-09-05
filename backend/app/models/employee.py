import enum
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"


class Employee(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "employees"

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
    )

    department_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )

    employee_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    hire_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    termination_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    job_title: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    status: Mapped[EmployeeStatus] = mapped_column(
        Enum(EmployeeStatus),
        default=EmployeeStatus.ACTIVE,
        nullable=False,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    emergency_contact_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    emergency_contact_phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    user: Mapped["User | None"] = relationship(
        back_populates="employee",
    )

    department: Mapped["Department | None"] = relationship(
        back_populates="employees",
    )

    contracts: Mapped[list["Contract"]] = relationship(
        back_populates="employee",
    )

    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="employee",
    )

    time_off_allocations: Mapped[list["TimeOffAllocation"]] = relationship(
        back_populates="employee",
    )

    time_off_requests: Mapped[list["TimeOffRequest"]] = relationship(
        back_populates="employee",
    )

    payslips: Mapped[list["Payslip"]] = relationship(
        back_populates="employee",
    )