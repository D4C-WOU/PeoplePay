from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.payslip import PayslipStatus
from app.schemas.payslip import PayslipResponse
from app.services import payslip_service
from app.services.pdf_service import generate_payslip_pdf

router=APIRouter(prefix="/payslips",tags=["Payslips"])
@router.get("",response_model=list[PayslipResponse])
def list_(employee_id:str|None=None,payrun_id:str|None=None,status:PayslipStatus|None=None,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    if user.role.value=="EMPLOYEE":employee_id=user.employee.id if user.employee else None
    else:require_permission(user,"payroll:read")
    return payslip_service.list_payslips(db,employee_id,payrun_id,status)
@router.get("/{id}",response_model=PayslipResponse)
def get(id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    try:obj=payslip_service.get_payslip(db,id)
    except ValueError as exc:raise HTTPException(404,str(exc))
    if user.role.value=="EMPLOYEE":
        if not user.employee or obj.employee_id!=user.employee.id:raise HTTPException(403,"Access denied")
    else:require_permission(user,"payroll:read")
    return obj
@router.get("/{id}/pdf")
def pdf(id:str,user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    try:obj=payslip_service.get_payslip(db,id)
    except ValueError as exc:raise HTTPException(404,str(exc))
    if user.role.value=="EMPLOYEE":
        if not user.employee or obj.employee_id!=user.employee.id:raise HTTPException(403,"Access denied")
    else:require_permission(user,"payroll:read")
    try:buf=generate_payslip_pdf(obj)
    except ValueError as exc:raise HTTPException(409,str(exc))
    return StreamingResponse(buf,media_type="application/pdf",headers={"Content-Disposition":f'attachment; filename="payslip-{obj.employee_number}.pdf"'})
