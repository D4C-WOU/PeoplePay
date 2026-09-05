from datetime import datetime, timezone
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.time_off import TimeOffAllocation, TimeOffRequest, TimeOffStatus, TimeOffType


def list_types(db): return db.scalars(select(TimeOffType).order_by(TimeOffType.name)).all()


def create_type(db, data):
    if db.scalar(select(TimeOffType).where(TimeOffType.code == data["code"])):
        raise ValueError("Time-off type code already exists")
    obj = TimeOffType(**data); db.add(obj); db.commit(); db.refresh(obj); return obj


def list_allocations(db, employee_id=None, year=None):
    stmt = select(TimeOffAllocation).order_by(TimeOffAllocation.year.desc())
    if employee_id: stmt = stmt.where(TimeOffAllocation.employee_id == employee_id)
    if year: stmt = stmt.where(TimeOffAllocation.year == year)
    return db.scalars(stmt).all()


def create_allocation(db, data):
    if not db.get(Employee, data["employee_id"]): raise ValueError("Employee not found")
    if not db.get(TimeOffType, data["time_off_type_id"]): raise ValueError("Time-off type not found")
    if db.scalar(select(TimeOffAllocation).where(
        TimeOffAllocation.employee_id == data["employee_id"],
        TimeOffAllocation.time_off_type_id == data["time_off_type_id"],
        TimeOffAllocation.year == data["year"],
    )): raise ValueError("Allocation already exists")
    obj = TimeOffAllocation(**data); db.add(obj); db.commit(); db.refresh(obj); return obj


def list_requests(db, employee_id=None, status=None):
    stmt = select(TimeOffRequest).order_by(TimeOffRequest.created_at.desc())
    if employee_id: stmt = stmt.where(TimeOffRequest.employee_id == employee_id)
    if status: stmt = stmt.where(TimeOffRequest.status == status)
    return db.scalars(stmt).all()


def create_request(db, data):
    if not db.get(Employee, data["employee_id"]): raise ValueError("Employee not found")
    if not db.get(TimeOffType, data["time_off_type_id"]): raise ValueError("Time-off type not found")
    overlap = db.scalar(select(TimeOffRequest).where(
        TimeOffRequest.employee_id == data["employee_id"],
        TimeOffRequest.status.in_([TimeOffStatus.PENDING, TimeOffStatus.APPROVED]),
        TimeOffRequest.start_date <= data["end_date"],
        TimeOffRequest.end_date >= data["start_date"],
    ))
    if overlap: raise ValueError("Time-off request overlaps an existing active request")
    obj = TimeOffRequest(**data); db.add(obj); db.commit(); db.refresh(obj); return obj


def transition(db, request: TimeOffRequest, target: TimeOffStatus, reviewer_id: str | None = None):
    allowed = {
        TimeOffStatus.PENDING: {TimeOffStatus.APPROVED, TimeOffStatus.REJECTED, TimeOffStatus.CANCELLED},
        TimeOffStatus.APPROVED: {TimeOffStatus.CANCELLED},
        TimeOffStatus.REJECTED: set(),
        TimeOffStatus.CANCELLED: set(),
    }
    if target not in allowed[request.status]: raise ValueError(f"Invalid time-off transition: {request.status} -> {target}")
    allocation = db.scalar(select(TimeOffAllocation).where(
        TimeOffAllocation.employee_id == request.employee_id,
        TimeOffAllocation.time_off_type_id == request.time_off_type_id,
        TimeOffAllocation.year == request.start_date.year,
    ).with_for_update())
    if target == TimeOffStatus.APPROVED:
        if not allocation or allocation.allocated_days - allocation.used_days < request.requested_days:
            raise ValueError("Insufficient time-off allocation")
        allocation.used_days += request.requested_days
    if request.status == TimeOffStatus.APPROVED and target == TimeOffStatus.CANCELLED and allocation:
        allocation.used_days = max(0, allocation.used_days - request.requested_days)
    request.status = target
    request.reviewed_by = reviewer_id
    request.reviewed_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(request); return request
