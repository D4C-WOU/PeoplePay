from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee, EmployeeStatus
from app.models.time_off import (
    TimeOffAllocation,
    TimeOffRequest,
    TimeOffStatus,
    TimeOffType,
)
from app.models.user import User


def _requested_days(start_date, end_date) -> Decimal:
    days = (end_date - start_date).days + 1

    if days <= 0:
        raise ValueError("Invalid time-off date range")

    return Decimal(days)


def get_request(
    db: Session,
    request_id: str,
) -> TimeOffRequest:
    request = db.get(
        TimeOffRequest,
        request_id,
    )

    if request is None:
        raise ValueError("Time-off request not found")

    return request


def list_requests(
    db: Session,
    employee_id: str | None = None,
    status: TimeOffStatus | None = None,
):
    stmt = select(TimeOffRequest).order_by(TimeOffRequest.created_at.desc())

    if employee_id:
        stmt = stmt.where(TimeOffRequest.employee_id == employee_id)

    if status:
        stmt = stmt.where(TimeOffRequest.status == status)

    return list(db.scalars(stmt).all())


def create_request(
    db: Session,
    data: dict,
) -> TimeOffRequest:

    employee = db.get(
        Employee,
        data["employee_id"],
    )

    if employee is None:
        raise ValueError("Employee not found")

    if employee.status == EmployeeStatus.TERMINATED:
        raise ValueError("Terminated employees cannot request time off")

    time_off_type = db.get(
        TimeOffType,
        data["time_off_type_id"],
    )

    if time_off_type is None:
        raise ValueError("Time-off type not found")

    if not time_off_type.is_active:
        raise ValueError("Time-off type is inactive")

    start_date = data["start_date"]
    end_date = data["end_date"]

    if start_date.year != end_date.year:
        raise ValueError("Time-off requests cannot cross calendar years")

    requested_days = _requested_days(
        start_date,
        end_date,
    )

    supplied_days = data.get("requested_days")

    if supplied_days is not None and Decimal(str(supplied_days)) != requested_days:
        raise ValueError(f"requested_days must equal {requested_days}")

    data["requested_days"] = requested_days

    request = TimeOffRequest(**data)

    db.add(request)

    try:
        db.commit()
        db.refresh(request)
        return request

    except IntegrityError:
        db.rollback()
        raise ValueError("Time-off request could not be created")


def approve_request(
    db: Session,
    request_id: str,
    reviewer_id: str,
) -> TimeOffRequest:

    request = get_request(
        db,
        request_id,
    )

    if request.status != TimeOffStatus.PENDING:
        raise ValueError("Only pending requests can be approved")

    reviewer = db.get(
        User,
        reviewer_id,
    )

    if reviewer is None or not reviewer.is_active:
        raise ValueError("Invalid reviewer")

    allocation = db.scalar(
        select(TimeOffAllocation)
        .where(
            TimeOffAllocation.employee_id == request.employee_id,
            TimeOffAllocation.time_off_type_id == request.time_off_type_id,
            TimeOffAllocation.year == request.start_date.year,
        )
        .with_for_update()
    )

    if allocation is None:
        raise ValueError("No time-off allocation exists for this employee and year")

    available = allocation.allocated_days - allocation.used_days

    if request.requested_days > available:
        raise ValueError("Insufficient time-off allocation")

    allocation.used_days += request.requested_days

    request.status = TimeOffStatus.APPROVED
    request.reviewed_by = reviewer_id
    request.reviewed_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(request)
        return request

    except Exception:
        db.rollback()
        raise


def reject_request(
    db: Session,
    request_id: str,
    reviewer_id: str,
) -> TimeOffRequest:

    request = get_request(
        db,
        request_id,
    )

    if request.status != TimeOffStatus.PENDING:
        raise ValueError("Only pending requests can be rejected")

    reviewer = db.get(
        User,
        reviewer_id,
    )

    if reviewer is None or not reviewer.is_active:
        raise ValueError("Invalid reviewer")

    request.status = TimeOffStatus.REJECTED
    request.reviewed_by = reviewer_id
    request.reviewed_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(request)
        return request

    except Exception:
        db.rollback()
        raise


def cancel_request(
    db: Session,
    request_id: str,
) -> TimeOffRequest:

    request = get_request(
        db,
        request_id,
    )

    if request.status == TimeOffStatus.CANCELLED:
        raise ValueError("Request is already cancelled")

    if request.status == TimeOffStatus.REJECTED:
        raise ValueError("Rejected requests cannot be cancelled")

    if request.status == TimeOffStatus.APPROVED:

        allocation = db.scalar(
            select(TimeOffAllocation)
            .where(
                TimeOffAllocation.employee_id == request.employee_id,
                TimeOffAllocation.time_off_type_id == request.time_off_type_id,
                TimeOffAllocation.year == request.start_date.year,
            )
            .with_for_update()
        )

        if allocation is None:
            raise ValueError("Allocation not found")

        if allocation.used_days < request.requested_days:
            raise ValueError("Invalid allocation balance")

        allocation.used_days -= request.requested_days

    request.status = TimeOffStatus.CANCELLED

    try:
        db.commit()
        db.refresh(request)
        return request

    except Exception:
        db.rollback()
        raise


def create_allocation(
    db: Session,
    data: dict,
) -> TimeOffAllocation:

    employee = db.get(
        Employee,
        data["employee_id"],
    )

    if employee is None:
        raise ValueError("Employee not found")

    if employee.status == EmployeeStatus.TERMINATED:
        raise ValueError("Terminated employees cannot receive allocations")

    time_off_type = db.get(
        TimeOffType,
        data["time_off_type_id"],
    )

    if time_off_type is None:
        raise ValueError("Time-off type not found")

    existing = db.scalar(
        select(TimeOffAllocation).where(
            TimeOffAllocation.employee_id == data["employee_id"],
            TimeOffAllocation.time_off_type_id == data["time_off_type_id"],
            TimeOffAllocation.year == data["year"],
        )
    )

    if existing:
        raise ValueError("Allocation already exists")

    allocation = TimeOffAllocation(**data)

    db.add(allocation)

    try:
        db.commit()
        db.refresh(allocation)
        return allocation

    except IntegrityError:
        db.rollback()
        raise ValueError("Allocation could not be created")


def list_allocations(
    db: Session,
    employee_id: str | None = None,
    year: int | None = None,
):
    stmt = select(TimeOffAllocation).order_by(TimeOffAllocation.year.desc())

    if employee_id:
        stmt = stmt.where(TimeOffAllocation.employee_id == employee_id)

    if year:
        stmt = stmt.where(TimeOffAllocation.year == year)

    return list(db.scalars(stmt).all())


def create_time_off_type(
    db: Session,
    data: dict,
):
    existing = db.scalar(select(TimeOffType).where(TimeOffType.code == data["code"]))

    if existing:
        raise ValueError("Time-off type code already exists")

    obj = TimeOffType(**data)
    db.add(obj)

    try:
        db.commit()
        db.refresh(obj)
        return obj

    except IntegrityError:
        db.rollback()
        raise ValueError("Time-off type could not be created")


def list_time_off_types(
    db: Session,
    active_only: bool = False,
):
    stmt = select(TimeOffType).order_by(TimeOffType.name)

    if active_only:
        stmt = stmt.where(TimeOffType.is_active.is_(True))

    return list(db.scalars(stmt).all())
