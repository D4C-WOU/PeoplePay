from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.time_off import (
    TimeOffAllocation,
    TimeOffRequest,
    TimeOffStatus,
    TimeOffType,
)
from app.models.user import User

# ============================================================
# TIME-OFF TYPES
# ============================================================


def list_types(db: Session) -> list[TimeOffType]:
    return db.scalars(select(TimeOffType).order_by(TimeOffType.name)).all()


def create_type(db: Session, data: dict) -> TimeOffType:
    existing = db.scalar(select(TimeOffType).where(TimeOffType.code == data["code"]))

    if existing is not None:
        raise ValueError("Time-off type code already exists")

    obj = TimeOffType(**data)

    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except Exception:
        db.rollback()
        raise


# ============================================================
# ALLOCATIONS
# ============================================================


def list_allocations(
    db: Session,
    employee_id: str | None = None,
    year: int | None = None,
) -> list[TimeOffAllocation]:

    stmt = select(TimeOffAllocation).order_by(TimeOffAllocation.year.desc())

    if employee_id:
        stmt = stmt.where(TimeOffAllocation.employee_id == employee_id)

    if year:
        stmt = stmt.where(TimeOffAllocation.year == year)

    return db.scalars(stmt).all()


def create_allocation(
    db: Session,
    data: dict,
) -> TimeOffAllocation:

    employee = db.get(Employee, data["employee_id"])

    if employee is None:
        raise ValueError("Employee not found")

    if employee.status.value == "TERMINATED":
        raise ValueError("Cannot create allocation for a terminated employee")

    time_off_type = db.get(
        TimeOffType,
        data["time_off_type_id"],
    )

    if time_off_type is None:
        raise ValueError("Time-off type not found")

    if not time_off_type.is_active:
        raise ValueError("Cannot create allocation for an inactive time-off type")

    existing = db.scalar(
        select(TimeOffAllocation).where(
            TimeOffAllocation.employee_id == data["employee_id"],
            TimeOffAllocation.time_off_type_id == data["time_off_type_id"],
            TimeOffAllocation.year == data["year"],
        )
    )

    if existing is not None:
        raise ValueError("Allocation already exists")

    obj = TimeOffAllocation(**data)

    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except Exception:
        db.rollback()
        raise


# ============================================================
# TIME-OFF REQUESTS
# ============================================================


def list_requests(
    db: Session,
    employee_id: str | None = None,
    status: TimeOffStatus | None = None,
) -> list[TimeOffRequest]:

    stmt = select(TimeOffRequest).order_by(TimeOffRequest.created_at.desc())

    if employee_id:
        stmt = stmt.where(TimeOffRequest.employee_id == employee_id)

    if status:
        stmt = stmt.where(TimeOffRequest.status == status)

    return db.scalars(stmt).all()


def _calculate_requested_days(
    start_date: date,
    end_date: date,
) -> Decimal:

    if end_date < start_date:
        raise ValueError("end_date cannot be before start_date")

    # Current business rule:
    # requested days are inclusive calendar days.
    days = (end_date - start_date).days + 1

    return Decimal(days)


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

    if employee.status.value == "TERMINATED":
        raise ValueError("Cannot create time-off request for a terminated employee")

    time_off_type = db.get(
        TimeOffType,
        data["time_off_type_id"],
    )

    if time_off_type is None:
        raise ValueError("Time-off type not found")

    if not time_off_type.is_active:
        raise ValueError("Cannot request an inactive time-off type")

    start_date = data["start_date"]
    end_date = data["end_date"]

    if end_date < start_date:
        raise ValueError("end_date cannot be before start_date")

    # We currently maintain allocations by year.
    # Until cross-year allocation splitting is implemented,
    # reject requests spanning multiple years.
    if start_date.year != end_date.year:
        raise ValueError("Time-off requests cannot span multiple years")

    calculated_days = _calculate_requested_days(
        start_date,
        end_date,
    )

    supplied_days = Decimal(str(data["requested_days"]))

    if supplied_days != calculated_days:
        raise ValueError(f"requested_days must equal {calculated_days}")

    overlap = db.scalar(
        select(TimeOffRequest).where(
            TimeOffRequest.employee_id == data["employee_id"],
            TimeOffRequest.status.in_(
                [
                    TimeOffStatus.PENDING,
                    TimeOffStatus.APPROVED,
                ]
            ),
            TimeOffRequest.start_date <= end_date,
            TimeOffRequest.end_date >= start_date,
        )
    )

    if overlap is not None:
        raise ValueError("Time-off request overlaps an existing active request")

    obj = TimeOffRequest(**data)

    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except Exception:
        db.rollback()
        raise


# ============================================================
# STATUS TRANSITIONS
# ============================================================


def transition(
    db: Session,
    request: TimeOffRequest,
    target: TimeOffStatus,
    reviewer_id: str | None = None,
) -> TimeOffRequest:

    allowed_transitions = {
        TimeOffStatus.PENDING: {
            TimeOffStatus.APPROVED,
            TimeOffStatus.REJECTED,
            TimeOffStatus.CANCELLED,
        },
        TimeOffStatus.APPROVED: {
            TimeOffStatus.CANCELLED,
        },
        TimeOffStatus.REJECTED: set(),
        TimeOffStatus.CANCELLED: set(),
    }

    if target not in allowed_transitions[request.status]:
        raise ValueError(
            f"Invalid time-off transition: " f"{request.status} -> {target}"
        )

    # --------------------------------------------------------
    # Validate reviewer
    # --------------------------------------------------------

    if reviewer_id is not None:
        reviewer = db.get(User, reviewer_id)

        if reviewer is None:
            raise ValueError("Reviewer not found")

        if not reviewer.is_active:
            raise ValueError("Inactive users cannot review time-off requests")

    # --------------------------------------------------------
    # APPROVAL
    # --------------------------------------------------------

    if target == TimeOffStatus.APPROVED:

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
            raise ValueError("No time-off allocation found for this employee and year")

        available_days = allocation.allocated_days - allocation.used_days

        if available_days < request.requested_days:
            raise ValueError("Insufficient time-off allocation")

        allocation.used_days += request.requested_days

    # --------------------------------------------------------
    # CANCELLING AN ALREADY APPROVED REQUEST
    # --------------------------------------------------------

    if request.status == TimeOffStatus.APPROVED and target == TimeOffStatus.CANCELLED:

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
            raise ValueError("Time-off allocation not found")

        new_used_days = allocation.used_days - request.requested_days

        if new_used_days < 0:
            raise ValueError("Time-off allocation would become negative")

        allocation.used_days = new_used_days

    # --------------------------------------------------------
    # UPDATE REQUEST
    # --------------------------------------------------------

    request.status = target

    request.reviewed_by = reviewer_id

    request.reviewed_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(request)
        return request

    except Exception:
        db.rollback()
        raise
