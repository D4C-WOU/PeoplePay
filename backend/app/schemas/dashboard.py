from decimal import Decimal
from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_employees: int
    active_employees: int
    employees_on_leave: int
    pending_time_off_requests: int
    current_payrun_status: str | None
    payroll_total_net: Decimal
    recent_payslips: int
