from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.time_off import (
    TimeOffRequest,
    TimeOffStatus,
)
from app.schemas.time_off import (
    AllocationCreate,
    AllocationResponse,
    TimeOffRequestCreate,
    TimeOffRequestResponse,
    TimeOffTypeCreate,
    TimeOffTypeResponse,
)
from app.services import time_off_service

router = APIRouter(
    prefix="/time-off",
    tags=["Time Off"],
)


def _is_employee(user) -> bool:
    return user.role.value == "EMPLOYEE"


@router.get(
    "/types",
    response_model=list[TimeOffTypeResponse],
)
def list_types(
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "timeoff:read",
    )

    return time_off_service.list_types(db)


@router.post(
    "/types",
    response_model=TimeOffTypeResponse,
    status_code=201,
)
def create_type(
    data: TimeOffTypeCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "timeoff:write",
    )

    try:
        return time_off_service.create_type(
            db,
            data.model_dump(),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.get(
    "/allocations",
    response_model=list[AllocationResponse],
)
def list_allocations(
    employee_id: str | None = None,
    year: int | None = None,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if _is_employee(user):
        if user.employee is None:
            return []

        employee_id = user.employee.id

    else:
        require_permission(
            user,
            "timeoff:read",
        )

    return time_off_service.list_allocations(
        db,
        employee_id,
        year,
    )


@router.post(
    "/allocations",
    response_model=AllocationResponse,
    status_code=201,
)
def create_allocation(
    data: AllocationCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(
        user,
        "timeoff:write",
    )

    try:
        return time_off_service.create_allocation(
            db,
            data.model_dump(),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.get(
    "/requests",
    response_model=list[TimeOffRequestResponse],
)
def list_requests(
    employee_id: str | None = None,
    status: TimeOffStatus | None = None,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if _is_employee(user):
        if user.employee is None:
            return []

        employee_id = user.employee.id

    else:
        require_permission(
            user,
            "timeoff:read",
        )

    return time_off_service.list_requests(
        db,
        employee_id,
        status,
    )


@router.post(
    "/requests",
    response_model=TimeOffRequestResponse,
    status_code=201,
)
def create_request(
    data: TimeOffRequestCreate,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if _is_employee(user):
        if user.employee is None or data.employee_id != user.employee.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )
    else:
        require_permission(
            user,
            "timeoff:write",
        )

    try:
        return time_off_service.create_request(
            db,
            data.model_dump(),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


def _transition(
    request_id: str,
    target: TimeOffStatus,
    user,
    db: Session,
):
    request = db.get(
        TimeOffRequest,
        request_id,
    )

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Time-off request not found",
        )

    # Employees may only cancel their own requests.
    if _is_employee(user):
        if target != TimeOffStatus.CANCELLED:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )

        if user.employee is None or request.employee_id != user.employee.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )

    else:
        require_permission(
            user,
            "timeoff:write",
        )

    try:
        return time_off_service.transition(
            db=db,
            request=request,
            target=target,
            reviewer_id=user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.post(
    "/requests/{request_id}/approve",
    response_model=TimeOffRequestResponse,
)
def approve_request(
    request_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return _transition(
        request_id,
        TimeOffStatus.APPROVED,
        user,
        db,
    )


@router.post(
    "/requests/{request_id}/reject",
    response_model=TimeOffRequestResponse,
)
def reject_request(
    request_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return _transition(
        request_id,
        TimeOffStatus.REJECTED,
        user,
        db,
    )


@router.post(
    "/requests/{request_id}/cancel",
    response_model=TimeOffRequestResponse,
)
def cancel_request(
    request_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return _transition(
        request_id,
        TimeOffStatus.CANCELLED,
        user,
        db,
    )
