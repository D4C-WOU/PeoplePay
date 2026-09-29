from decimal import Decimal

from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncMonth

from attendance.models import AttendanceRecord
from employees.models import Department, Employee
from payroll.models import Payslip
from time_off.models import TimeOffRequest


def get_dashboard_data():
    # Get employees with their department loaded
    employees = Employee.objects.select_related("department")

    # Count employees by their actual employee status
    total_employees = employees.count()

    active_employees = employees.filter(
        status=Employee.Status.ACTIVE,
    ).count()

    on_leave_employees = employees.filter(
        status=Employee.Status.ON_LEAVE,
    ).count()

    # Get paid payslips for payroll statistics
    paid_payslips = Payslip.objects.filter(
        status=Payslip.Status.PAID,
    )

    # Calculate total net salary already paid
    total_net_paid = paid_payslips.aggregate(
        total=Sum("net_amount"),
    )[
        "total"
    ] or Decimal("0.00")

    # Count all generated payslips
    payslips_generated = Payslip.objects.count()

    # Calculate average net salary from paid payslips
    average_salary = paid_payslips.aggregate(
        average=Avg("net_amount"),
    )[
        "average"
    ] or Decimal("0.00")

    # Get all attendance records
    attendance_records = AttendanceRecord.objects.all()

    attendance_total = attendance_records.count()

    attendance_present = attendance_records.filter(
        status=AttendanceRecord.Status.PRESENT,
    ).count()

    attendance_absent = attendance_records.filter(
        status=AttendanceRecord.Status.ABSENT,
    ).count()

    attendance_half_day = attendance_records.filter(
        status=AttendanceRecord.Status.HALF_DAY,
    ).count()

    attendance_late = attendance_records.filter(
        status=AttendanceRecord.Status.LATE,
    ).count()

    attendance_on_leave = attendance_records.filter(
        status=AttendanceRecord.Status.ON_LEAVE,
    ).count()

    # Calculate the percentage of attendance records that were not absent
    if attendance_total:
        attendance_health = (
            (attendance_total - attendance_absent) / attendance_total
        ) * 100
    else:
        attendance_health = Decimal("0.00")

    # Count time-off requests by their workflow status
    approved_time_off = TimeOffRequest.objects.filter(
        status=TimeOffRequest.Status.APPROVED,
    ).count()

    pending_time_off = TimeOffRequest.objects.filter(
        status=TimeOffRequest.Status.PENDING,
    ).count()

    rejected_time_off = TimeOffRequest.objects.filter(
        status=TimeOffRequest.Status.REJECTED,
    ).count()

    # Build department-wise employee counts
    department_data = []

    for department in Department.objects.all().order_by("name"):
        department_employees = employees.filter(
            department=department,
        )

        department_data.append(
            {
                "id": department.id,
                "name": department.name,
                "employee_count": department_employees.count(),
                "active_employee_count": department_employees.filter(
                    status=Employee.Status.ACTIVE,
                ).count(),
            }
        )

    # Group paid salary by month
    monthly_salary_data = (
        paid_payslips.annotate(
            month=TruncMonth("period_start"),
        )
        .values("month")
        .annotate(
            net_salary=Sum("net_amount"),
            payslip_count=Count("id"),
        )
        .order_by("month")
    )

    monthly_salary_trend = []

    for item in monthly_salary_data:
        monthly_salary_trend.append(
            {
                "month": item["month"].strftime("%Y-%m"),
                "net_salary": item["net_salary"] or Decimal("0.00"),
                "payslip_count": item["payslip_count"],
            }
        )

    # Return all dashboard sections as one response
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
            "health_percentage": round(
                float(attendance_health),
                2,
            ),
        },
        "time_off": {
            "approved": approved_time_off,
            "pending": pending_time_off,
            "rejected": rejected_time_off,
        },
        "departments": department_data,
        "monthly_salary_trend": monthly_salary_trend,
    }
