from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncMonth

from attendance.models import AttendanceRecord
from contracts.models import Contract
from employees.models import Department, Employee
from payroll.models import Payslip
from time_off.models import TimeOffAllocation, TimeOffRequest


def get_dashboard_data(
    period_start=None, period_end=None, department_id=None, employee_type=None
):
    # Apply the same filters to every module so the dashboard remains consistent.
    employees = Employee.objects.select_related("department")
    if department_id:
        employees = employees.filter(department_id=department_id)
    if employee_type:
        employees = employees.filter(employee_type=employee_type)

    employee_ids = employees.values_list("id", flat=True)

    paid_payslips = Payslip.objects.filter(
        status=Payslip.Status.PAID, employee_id__in=employee_ids
    )
    all_payslips = Payslip.objects.filter(employee_id__in=employee_ids)
    attendance_records = AttendanceRecord.objects.filter(employee_id__in=employee_ids)
    time_off_requests = TimeOffRequest.objects.filter(employee_id__in=employee_ids)

    if period_start:
        paid_payslips = paid_payslips.filter(period_end__gte=period_start)
        all_payslips = all_payslips.filter(period_end__gte=period_start)
        attendance_records = attendance_records.filter(
            attendance_date__gte=period_start
        )
        time_off_requests = time_off_requests.filter(end_date__gte=period_start)
    if period_end:
        paid_payslips = paid_payslips.filter(period_start__lte=period_end)
        all_payslips = all_payslips.filter(period_start__lte=period_end)
        attendance_records = attendance_records.filter(attendance_date__lte=period_end)
        time_off_requests = time_off_requests.filter(start_date__lte=period_end)

    total_employees = employees.count()
    active_employees = employees.filter(status=Employee.Status.ACTIVE).count()
    on_leave_employees = employees.filter(status=Employee.Status.ON_LEAVE).count()

    total_net_paid = paid_payslips.aggregate(total=Sum("net_amount"))[
        "total"
    ] or Decimal("0.00")
    payslips_generated = all_payslips.count()
    average_salary = paid_payslips.aggregate(average=Avg("net_amount"))[
        "average"
    ] or Decimal("0.00")

    attendance_total = attendance_records.count()
    attendance_present = attendance_records.filter(
        status=AttendanceRecord.Status.PRESENT
    ).count()
    attendance_absent = attendance_records.filter(
        status=AttendanceRecord.Status.ABSENT
    ).count()
    attendance_half_day = attendance_records.filter(
        status=AttendanceRecord.Status.HALF_DAY
    ).count()
    attendance_late = attendance_records.filter(
        status=AttendanceRecord.Status.LATE
    ).count()
    attendance_on_leave = attendance_records.filter(
        status=AttendanceRecord.Status.ON_LEAVE
    ).count()
    overtime_hours = attendance_records.aggregate(total=Sum("overtime_hours"))[
        "total"
    ] or Decimal("0.00")
    missing_checkouts = attendance_records.filter(
        check_in__isnull=False, check_out__isnull=True
    ).count()
    attendance_health = (
        ((attendance_total - attendance_absent) / attendance_total * 100)
        if attendance_total
        else Decimal("0.00")
    )

    approved_time_off = time_off_requests.filter(
        status=TimeOffRequest.Status.APPROVED
    ).count()
    pending_time_off = time_off_requests.filter(
        status=TimeOffRequest.Status.PENDING
    ).count()
    rejected_time_off = time_off_requests.filter(
        status=TimeOffRequest.Status.REJECTED
    ).count()

    department_data = []
    for department in Department.objects.all().order_by("name"):
        department_employees = employees.filter(department=department)
        department_salary = paid_payslips.filter(
            employee__department=department
        ).aggregate(total=Sum("net_amount"))["total"] or Decimal("0.00")
        department_data.append(
            {
                "id": department.id,
                "name": department.name,
                "employee_count": department_employees.count(),
                "active_employee_count": department_employees.filter(
                    status=Employee.Status.ACTIVE
                ).count(),
                "salary_expenditure": department_salary,
            }
        )

    monthly_salary_data = (
        paid_payslips.annotate(month=TruncMonth("period_start"))
        .values("month")
        .annotate(net_salary=Sum("net_amount"), payslip_count=Count("id"))
        .order_by("month")
    )
    monthly_salary_trend = [
        {
            "month": item["month"].strftime("%Y-%m"),
            "net_salary": item["net_salary"] or Decimal("0.00"),
            "payslip_count": item["payslip_count"],
        }
        for item in monthly_salary_data
    ]

    duplicate_payslips = (
        all_payslips.values("employee", "period_start", "period_end")
        .annotate(count=Count("id"))
        .filter(count__gt=1)
        .count()
    )
    missing_bank_details = (
        employees.filter(status=Employee.Status.ACTIVE)
        .filter(bank_account_number__isnull=True)
        .count()
    )
    contracts_attention = Contract.objects.filter(
        employee_id__in=employee_ids,
        status=Contract.Status.ACTIVE,
        end_date__isnull=False,
        end_date__lte=date.today() + timedelta(days=30),
        end_date__gte=date.today(),
    ).count()

    leave_balance = TimeOffAllocation.objects.filter(
        employee_id__in=employee_ids,
        status=TimeOffAllocation.Status.APPROVED,
    ).aggregate(remaining=Sum("allocated_days") - Sum("used_days"))[
        "remaining"
    ] or Decimal(
        "0.00"
    )

    return {
        "employees": {
            "total": total_employees,
            "active": active_employees,
            "on_leave": on_leave_employees,
        },
        "payroll": {
            "total_net_paid": total_net_paid,
            "payslips_generated": payslips_generated,
            "average_salary": average_salary,
        },
        "attendance": {
            "total": attendance_total,
            "present": attendance_present,
            "absent": attendance_absent,
            "half_day": attendance_half_day,
            "late": attendance_late,
            "on_leave": attendance_on_leave,
            "health_percentage": round(float(attendance_health), 2),
            "overtime_hours": overtime_hours,
            "missing_checkouts": missing_checkouts,
        },
        "time_off": {
            "approved": approved_time_off,
            "pending": pending_time_off,
            "rejected": rejected_time_off,
            "remaining_balance": leave_balance,
        },
        "departments": department_data,
        "monthly_salary_trend": monthly_salary_trend,
        "warnings": {
            "missing_bank_details": missing_bank_details,
            "duplicate_payslips": duplicate_payslips,
            "contracts_attention": contracts_attention,
        },
    }
