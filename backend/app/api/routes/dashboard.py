from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.models.employee import Employee, EmployeeStatus, EmployeeType
from app.models.department import Department
from app.models.payrun import Payrun
from app.models.payslip import Payslip, PayslipStatus
from app.models.time_off import TimeOffRequest, TimeOffStatus
from app.schemas.dashboard import DashboardResponse, DepartmentSalaryCost

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def dashboard(
    employee_type: EmployeeType | None = None,
    user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    require_permission(user, "dashboard:read")

    employee_filter = []
    if employee_type is not None:
        employee_filter.append(Employee.employee_type == employee_type)

    def count_employees(condition=None):
        stmt = select(func.count()).select_from(Employee)
        if employee_filter:
            stmt = stmt.where(*employee_filter)
        if condition is not None:
            stmt = stmt.where(condition)
        return db.scalar(stmt) or 0

    total = count_employees()
    active = count_employees(Employee.status == EmployeeStatus.ACTIVE)
    leave = count_employees(Employee.status == EmployeeStatus.ON_LEAVE)

    pending = (
        db.scalar(
            select(func.count())
            .select_from(TimeOffRequest)
            .where(TimeOffRequest.status == TimeOffStatus.PENDING)
        )
        or 0
    )
    approved = (
        db.scalar(
            select(func.count())
            .select_from(TimeOffRequest)
            .where(TimeOffRequest.status == TimeOffStatus.APPROVED)
        )
        or 0
    )

    run = db.scalar(select(Payrun).order_by(Payrun.period_start.desc()).limit(1))
    total_net_paid = db.scalar(
        select(func.coalesce(func.sum(Payslip.net_amount), 0)).where(
            Payslip.status == PayslipStatus.PAID
        )
    ) or Decimal("0")
    average_salary = db.scalar(
        select(func.coalesce(func.avg(Payslip.net_amount), 0)).where(
            Payslip.status.in_([PayslipStatus.FINALIZED, PayslipStatus.PAID])
        )
    ) or Decimal("0")

    attendance_total = (
        db.scalar(select(func.count()).select_from(AttendanceRecord)) or 0
    )
    present = (
        db.scalar(
            select(func.count())
            .select_from(AttendanceRecord)
            .where(AttendanceRecord.status == AttendanceStatus.PRESENT)
        )
        or 0
    )
    absent = (
        db.scalar(
            select(func.count())
            .select_from(AttendanceRecord)
            .where(AttendanceRecord.status == AttendanceStatus.ABSENT)
        )
        or 0
    )
    attendance_health = (
        (Decimal(present) / Decimal(attendance_total) * Decimal("100"))
        if attendance_total
        else Decimal("0")
    )
    attendance_health = attendance_health.quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    department_rows = db.execute(
        select(Employee.department_id, func.coalesce(func.sum(Payslip.net_amount), 0))
        .join(Payslip, Payslip.employee_id == Employee.id)
        .where(Payslip.status.in_([PayslipStatus.FINALIZED, PayslipStatus.PAID]))
        .group_by(Employee.department_id)
    ).all()
    department_names = {
        department.id: department.name
        for department in db.scalars(select(Department)).all()
    }
    department_salary_costs = [
        DepartmentSalaryCost(
            department_id=department_id,
            department_name=department_names.get(department_id, "Unassigned"),
            total_salary=total_salary,
        )
        for department_id, total_salary in department_rows
    ]

    recent = db.scalar(select(func.count()).select_from(Payslip)) or 0

    return DashboardResponse(
        total_employees=total,
        active_employees=active,
        employees_on_leave=leave,
        pending_time_off_requests=pending,
        approved_time_off_requests=approved,
        current_payrun_status=run.status.value if run else None,
        payroll_total_net=run.total_net if run else Decimal("0"),
        total_net_paid=total_net_paid,
        average_salary=average_salary,
        total_attendance_records=attendance_total,
        present_attendance=present,
        absent_attendance=absent,
        attendance_health=attendance_health,
        recent_payslips=recent,
        department_salary_costs=department_salary_costs,
    )
