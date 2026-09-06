from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.attendance import (
    AttendanceRecord,
    AttendanceStatus,
)
from app.models.employee import Employee
from app.models.work_schedule import WorkSchedule
from app.schemas.pagination import Page
from app.utils.calculations import (
    calculate_overtime,
    calculate_worked_hours,
)
from app.utils.pagination import paginate_scalars


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None or value.tzinfo is None:
        return value

    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _validate_employee(
    db: Session,
    employee_id: str,
) -> Employee:
    employee = db.get(
        Employee,
        employee_id,
    )

    if employee is None:
        raise ValueError("Employee not found")

    return employee


def _validate_schedule(
    db: Session,
    work_schedule_id: str | None,
) -> None:
    if work_schedule_id is None:
        return

    schedule = db.get(
        WorkSchedule,
        work_schedule_id,
    )

    if schedule is None:
        raise ValueError("Work schedule not found")

    if not schedule.is_active:
        raise ValueError("Work schedule is inactive")


def _validate_hours(
    expected_hours,
    worked_hours,
    overtime_hours,
) -> None:
    if expected_hours < 0:
        raise ValueError("Expected hours cannot be negative")

    if worked_hours < 0:
        raise ValueError("Worked hours cannot be negative")

    if overtime_hours < 0:
        raise ValueError("Overtime hours cannot be negative")


def create_attendance(
    db: Session,
    data: dict,
) -> AttendanceRecord:
    employee = _validate_employee(
        db,
        data["employee_id"],
    )

    if employee.status.value == "TERMINATED":
        raise ValueError("Cannot create attendance for a terminated employee")

    _validate_schedule(
        db,
        data.get("work_schedule_id"),
    )

    existing = db.scalar(
        select(AttendanceRecord).where(
            AttendanceRecord.employee_id == data["employee_id"],
            AttendanceRecord.attendance_date == data["attendance_date"],
        )
    )

    if existing is not None:
        raise ValueError("Attendance already exists for this employee/date")

    check_in = data.get("check_in")
    check_out = data.get("check_out")

    data["check_in"] = _normalize_datetime(check_in)
    data["check_out"] = _normalize_datetime(check_out)
    check_in = data["check_in"]
    check_out = data["check_out"]

    if check_in is not None and check_out is not None and check_out < check_in:
        raise ValueError("check_out cannot be before check_in")

    expected_hours = data.get(
        "expected_hours",
        0,
    )

    expected_hours = data.get(
        "expected_hours",
        0,
    )

    worked_hours = calculate_worked_hours(
        check_in,
        check_out,
    )

    overtime_hours = calculate_overtime(
        worked_hours,
        expected_hours,
    )
    _validate_hours(
        expected_hours,
        worked_hours,
        overtime_hours,
    )

    data["expected_hours"] = expected_hours
    data["worked_hours"] = worked_hours
    data["overtime_hours"] = overtime_hours

    record = AttendanceRecord(**data)

    db.add(record)

    try:
        db.commit()
        db.refresh(record)

    except IntegrityError:
        db.rollback()
        raise ValueError("Attendance already exists for this employee/date")

    return record


def list_attendance(
    db: Session,
    employee_id: str | None = None,
    attendance_date=None,
    start_date=None,
    end_date=None,
    status: AttendanceStatus | None = None,
    page: int | None = None,
    page_size: int = 10,
) -> list[AttendanceRecord] | Page[AttendanceRecord]:
    if start_date is not None and end_date is not None and end_date < start_date:
        raise ValueError("end_date cannot be before start_date")

    stmt = select(AttendanceRecord).order_by(AttendanceRecord.attendance_date.desc())

    if employee_id is not None:
        stmt = stmt.where(AttendanceRecord.employee_id == employee_id)

    if attendance_date is not None:
        stmt = stmt.where(AttendanceRecord.attendance_date == attendance_date)

    if start_date is not None:
        stmt = stmt.where(AttendanceRecord.attendance_date >= start_date)

    if end_date is not None:
        stmt = stmt.where(AttendanceRecord.attendance_date <= end_date)

    if status is not None:
        stmt = stmt.where(AttendanceRecord.status == status)

    if page is not None:
        return paginate_scalars(db, stmt, page, page_size)

    return list(db.scalars(stmt).all())


def update_attendance(
    db: Session,
    record: AttendanceRecord,
    data: dict,
) -> AttendanceRecord:
    if "check_in" in data:
        data["check_in"] = _normalize_datetime(data["check_in"])
    if "check_out" in data:
        data["check_out"] = _normalize_datetime(data["check_out"])

    if "work_schedule_id" in data:
        _validate_schedule(
            db,
            data["work_schedule_id"],
        )

    for field, value in data.items():
        setattr(
            record,
            field,
            value,
        )

    if (
        record.check_in is not None
        and record.check_out is not None
        and record.check_out < record.check_in
    ):
        raise ValueError("check_out cannot be before check_in")

    if "check_in" in data or "check_out" in data or "expected_hours" in data:
        record.worked_hours = calculate_worked_hours(
            record.check_in,
            record.check_out,
        )

        record.overtime_hours = calculate_overtime(
            record.worked_hours,
            record.expected_hours,
        )

    _validate_hours(
        record.expected_hours,
        record.worked_hours,
        record.overtime_hours,
    )

    try:
        db.commit()
        db.refresh(record)

    except IntegrityError:
        db.rollback()
        raise ValueError("Attendance could not be updated")

    return record
