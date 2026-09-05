from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.employee import Employee,EmployeeStatus
from app.models.payrun import Payrun,PayrunStatus
from app.models.payslip import Payslip
from app.models.time_off import TimeOffRequest,TimeOffStatus
from app.schemas.dashboard import DashboardResponse

router=APIRouter(prefix="/dashboard",tags=["Dashboard"])
@router.get("",response_model=DashboardResponse)
def dashboard(user=Depends(get_current_active_user),db:Session=Depends(get_db)):
    require_permission(user,"dashboard:read")
    total=db.scalar(select(func.count()).select_from(Employee)) or 0
    active=db.scalar(select(func.count()).select_from(Employee).where(Employee.status==EmployeeStatus.ACTIVE)) or 0
    leave=db.scalar(select(func.count()).select_from(Employee).where(Employee.status==EmployeeStatus.ON_LEAVE)) or 0
    pending=db.scalar(select(func.count()).select_from(TimeOffRequest).where(TimeOffRequest.status==TimeOffStatus.PENDING)) or 0
    run=db.scalar(select(Payrun).order_by(Payrun.period_start.desc()).limit(1))
    recent=db.scalar(select(func.count()).select_from(Payslip)) or 0
    return DashboardResponse(total_employees=total,active_employees=active,employees_on_leave=leave,
      pending_time_off_requests=pending,current_payrun_status=run.status.value if run else None,
      payroll_total_net=run.total_net if run else 0,recent_payslips=recent)
