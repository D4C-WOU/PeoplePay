from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.schemas.time_off import (
    AllocationCreate,
    AllocationResponse,
    TimeOffRequestCreate,
    TimeOffRequestResponse,
    TimeOffTypeCreate,
    TimeOffTypeResponse,
)
from app.models.time_off import TimeOffStatus
from app.services import time_off_service

router = APIRouter(
    prefix="/time-off",
    tags=["Time Off"],
)


@router.get(
    "/types",
    response_model=list[TimeOffTypeResponse],
)
def list_types(
    active_only: bool = False,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "timeoff:read")

    return time_off_service.list_time_off_types(
        db,
        active_only,
    )


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
    require_permission(user, "timeoff:write")

    try:
        return time_off_service.create_time_off_type(
            db,
            data.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


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
    require_permission(user, "timeoff:read")

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
    require_permission(user, "timeoff:write")

    try:
        return time_off_service.create_allocation(
            db,
            data.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


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
    require_permission(user, "timeoff:read")

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
    require_permission(user, "timeoff:write")

    try:
        return time_off_service.create_request(
            db,
            data.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.get(
    "/requests/{request_id}",
    response_model=TimeOffRequestResponse,
)
def get_request(
    request_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "timeoff:read")

    try:
        return time_off_service.get_request(
            db,
            request_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post(
    "/requests/{request_id}/approve",
    response_model=TimeOffRequestResponse,
)
def approve_request(
    request_id: str,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "timeoff:write")

    try:
        return time_off_service.approve_request(
            db,
            request_id,
            str(user.id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
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
    require_permission(user, "timeoff:write")

    try:
        return time_off_service.reject_request(
            db,
            request_id,
            str(user.id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
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
    require_permission(user, "timeoff:write")

    try:
        return time_off_service.cancel_request(
            db,
            request_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )
