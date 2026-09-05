from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.attendance import AttendanceStatus
from app.schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceUpdate
from app.services import attendance_service

router=APIRouter(prefix="/attendance",tags=["Attendance"])

@router.get("",response_model=list[AttendanceResponse])
def list_records(employee_id:str|None=None,attendance_date:date|None=None,start_date:date|None=None,end_date:date|None=None,status:AttendanceStatus|None=None,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    if user.role.value=="EMPLOYEE":
        if not user.employee: return []
        employee_id=user.employee.id
    else: require_permission(user,"attendance:read")
    return attendance_service.list_attendance(db,employee_id,attendance_date,start_date,end_date,status)

@router.post("",response_model=AttendanceResponse,status_code=201)
def create(data:AttendanceCreate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    if user.role.value=="EMPLOYEE":
        if not user.employee or data.employee_id != user.employee.id: raise HTTPException(403,"Access denied")
    else: require_permission(user,"attendance:write")
    try:return attendance_service.create_attendance(db,data.model_dump())
    except ValueError as exc:raise HTTPException(409,str(exc))

@router.get("/{record_id}",response_model=AttendanceResponse)
def get(record_id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    obj=db.get(__import__("app.models.attendance",fromlist=["AttendanceRecord"]).AttendanceRecord,record_id)
    if not obj:raise HTTPException(404,"Attendance record not found")
    if user.role.value=="EMPLOYEE" and (not user.employee or obj.employee_id!=user.employee.id):raise HTTPException(403,"Access denied")
    if user.role.value!="EMPLOYEE":require_permission(user,"attendance:read")
    return obj

@router.patch("/{record_id}",response_model=AttendanceResponse)
def update(record_id:str,data:AttendanceUpdate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    from app.models.attendance import AttendanceRecord
    obj=db.get(AttendanceRecord,record_id)
    if not obj:raise HTTPException(404,"Attendance record not found")
    if user.role.value=="EMPLOYEE" and (not user.employee or obj.employee_id!=user.employee.id):raise HTTPException(403,"Access denied")
    if user.role.value!="EMPLOYEE":require_permission(user,"attendance:write")
    try:return attendance_service.update_attendance(db,obj,data.model_dump(exclude_unset=True))
    except ValueError as exc:raise HTTPException(409,str(exc))
