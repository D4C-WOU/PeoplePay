from decimal import Decimal

from pydantic import BaseModel


class DepartmentSalaryCost(BaseModel):
    department_id: str | None
    department_name: str
    total_salary: Decimal


class DashboardResponse(BaseModel):
    total_employees: int
    active_employees: int
    employees_on_leave: int

    pending_time_off_requests: int
    approved_time_off_requests: int

    current_payrun_status: str | None

    payroll_total_net: Decimal
    total_net_paid: Decimal

    average_salary: Decimal

    total_attendance_records: int
    present_attendance: int
    absent_attendance: int
    attendance_health: Decimal

    recent_payslips: int

    department_salary_costs: list[DepartmentSalaryCost]
