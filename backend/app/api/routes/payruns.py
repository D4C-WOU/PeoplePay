from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.payrun import PayrunStatus
from app.schemas.payrun import PayrunCreate,PayrunResponse
from app.services import payroll_service

router=APIRouter(prefix="/payruns",tags=["Payroll"])
@router.get("",response_model=list[PayrunResponse])
def list_(status:PayrunStatus|None=None,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"payroll:read");return payroll_service.list_payruns(db,status)
@router.post("",response_model=PayrunResponse,status_code=201)
def create(data:PayrunCreate,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"payroll:write")
    try:return payroll_service.create_payrun(db,**data.model_dump())
    except ValueError as exc:raise HTTPException(409,str(exc))
@router.get("/{id}",response_model=PayrunResponse)
def get(id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"payroll:read")
    try:return payroll_service.get_payrun(db,id)
    except ValueError as exc:raise HTTPException(404,str(exc))
@router.post("/{id}/process",response_model=PayrunResponse)
def process(id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"payroll:write")
    try:return payroll_service.process_payrun(db,payroll_service.get_payrun(db,id))
    except ValueError as exc:raise HTTPException(409,str(exc))
@router.post("/{id}/finalize",response_model=PayrunResponse)
def finalize(id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"payroll:write")
    try:return payroll_service.finalize_payrun(db,payroll_service.get_payrun(db,id))
    except ValueError as exc:raise HTTPException(409,str(exc))
@router.post("/{id}/cancel",response_model=PayrunResponse)
def cancel(id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"payroll:write")
    try:return payroll_service.cancel_payrun(db,payroll_service.get_payrun(db,id))
    except ValueError as exc:raise HTTPException(409,str(exc))
