from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.models.employee import Employee
from app.models.work_schedule import WorkSchedule
from app.utils.calculations import calculate_overtime, calculate_worked_hours


def _validate_employee(db, employee_id):
    if not db.get(Employee, employee_id):
        raise ValueError("Employee not found")


def create_attendance(db: Session, data: dict) -> AttendanceRecord:
    _validate_employee(db, data["employee_id"])
    if data.get("work_schedule_id") and not db.get(WorkSchedule, data["work_schedule_id"]):
        raise ValueError("Work schedule not found")
    if db.scalar(select(AttendanceRecord).where(
        AttendanceRecord.employee_id == data["employee_id"],
        AttendanceRecord.attendance_date == data["attendance_date"],
    )):
        raise ValueError("Attendance already exists for this employee/date")
    worked = data.get("worked_hours")
    if worked is None:
        worked = calculate_worked_hours(data.get("check_in"), data.get("check_out"))
    overtime = data.get("overtime_hours")
    if overtime is None:
        overtime = calculate_overtime(worked, data.get("expected_hours", 0))
    data["worked_hours"], data["overtime_hours"] = worked, overtime
    record = AttendanceRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_attendance(db: Session, employee_id=None, attendance_date=None, start_date=None, end_date=None, status=None):
    stmt = select(AttendanceRecord).order_by(AttendanceRecord.attendance_date.desc())
    if employee_id: stmt = stmt.where(AttendanceRecord.employee_id == employee_id)
    if attendance_date: stmt = stmt.where(AttendanceRecord.attendance_date == attendance_date)
    if start_date: stmt = stmt.where(AttendanceRecord.attendance_date >= start_date)
    if end_date: stmt = stmt.where(AttendanceRecord.attendance_date <= end_date)
    if status: stmt = stmt.where(AttendanceRecord.status == status)
    return db.scalars(stmt).all()


def update_attendance(db: Session, record: AttendanceRecord, data: dict) -> AttendanceRecord:
    for k, v in data.items(): setattr(record, k, v)
    if record.check_in and record.check_out and record.check_out < record.check_in:
        raise ValueError("check_out cannot be before check_in")
    if "check_in" in data or "check_out" in data or "expected_hours" in data:
        record.worked_hours = calculate_worked_hours(record.check_in, record.check_out)
        record.overtime_hours = calculate_overtime(record.worked_hours, record.expected_hours)
    db.commit(); db.refresh(record)
    return record
