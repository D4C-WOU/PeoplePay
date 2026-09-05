from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.time_off import TimeOffStatus
from app.schemas.time_off import AllocationCreate, AllocationResponse, TimeOffRequestCreate, TimeOffRequestResponse, TimeOffTypeCreate, TimeOffTypeResponse
from app.services import time_off_service

router=APIRouter(prefix="/time-off",tags=["Time Off"])

@router.get("/types",response_model=list[TimeOffTypeResponse])
def types(user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"timeoff:read");return time_off_service.list_types(db)

@router.post("/types",response_model=TimeOffTypeResponse,status_code=201)
def create_type(data:TimeOffTypeCreate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"timeoff:write")
    try:return time_off_service.create_type(db,data.model_dump())
    except ValueError as exc:raise HTTPException(409,str(exc))

@router.get("/allocations",response_model=list[AllocationResponse])
def allocations(employee_id:str|None=None,year:int|None=None,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    if user.role.value=="EMPLOYEE": employee_id=user.employee.id if user.employee else None
    else:require_permission(user,"timeoff:read")
    return time_off_service.list_allocations(db,employee_id,year)

@router.post("/allocations",response_model=AllocationResponse,status_code=201)
def create_allocation(data:AllocationCreate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"timeoff:write")
    try:return time_off_service.create_allocation(db,data.model_dump())
    except ValueError as exc:raise HTTPException(409,str(exc))

@router.get("/requests",response_model=list[TimeOffRequestResponse])
def requests(employee_id:str|None=None,status:TimeOffStatus|None=None,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    if user.role.value=="EMPLOYEE": employee_id=user.employee.id if user.employee else None
    else:require_permission(user,"timeoff:read")
    return time_off_service.list_requests(db,employee_id,status)

@router.post("/requests",response_model=TimeOffRequestResponse,status_code=201)
def create_request(data:TimeOffRequestCreate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    if user.role.value=="EMPLOYEE":
        if not user.employee or data.employee_id!=user.employee.id:raise HTTPException(403,"Access denied")
    else:require_permission(user,"timeoff:write")
    try:return time_off_service.create_request(db,data.model_dump())
    except ValueError as exc:raise HTTPException(409,str(exc))

def _transition(request_id,target,user,db):
    obj=next((x for x in time_off_service.list_requests(db) if x.id==request_id),None)
    if not obj:raise HTTPException(404,"Time-off request not found")
    if target==TimeOffStatus.CANCELLED and user.role.value=="EMPLOYEE":
        if not user.employee or obj.employee_id!=user.employee.id:raise HTTPException(403,"Access denied")
    else: require_permission(user,"timeoff:write")
    try:return time_off_service.transition(db,obj,target,user.id)
    except ValueError as exc:raise HTTPException(409,str(exc))

@router.post("/requests/{request_id}/approve",response_model=TimeOffRequestResponse)
def approve(request_id,user=Depends(get_current_active_user),db:Session=Depends(get_db)): return _transition(request_id,TimeOffStatus.APPROVED,user,db)
@router.post("/requests/{request_id}/reject",response_model=TimeOffRequestResponse)
def reject(request_id,user=Depends(get_current_active_user),db:Session=Depends(get_db)): return _transition(request_id,TimeOffStatus.REJECTED,user,db)
@router.post("/requests/{request_id}/cancel",response_model=TimeOffRequestResponse)
def cancel(request_id,user=Depends(get_current_active_user),db:Session=Depends(get_db)): return _transition(request_id,TimeOffStatus.CANCELLED,user,db)
