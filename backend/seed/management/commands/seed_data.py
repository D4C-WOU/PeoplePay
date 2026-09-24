from datetime import date, datetime, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from users.models import User
from employees.models import (
    Department,
    Employee,
    WorkSchedule,
    WorkScheduleDay,
)
from contracts.models import Contract
from attendance.models import AttendanceRecord
from time_off.models import (
    TimeOffType,
    TimeOffAllocation,
)
from payroll.models import SalaryStructure, SalaryRule


class Command(BaseCommand):
    help = "Create representative PeoplePay360 HR and payroll data."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting PeoplePay360 seed data...")

        departments = self.seed_departments()
        schedules = self.seed_schedules()
        users = self.seed_users()
        employees = self.seed_employees(
            departments,
            schedules,
            users,
        )

        # Salary structure is needed before creating contracts.
        self.seed_salary_data()

        self.seed_contracts(
            employees,
            schedules,
        )

        self.seed_attendance(
            employees,
            schedules,
        )

        self.seed_time_off()
        self.seed_allocations(employees)

        self.stdout.write(
            self.style.SUCCESS("PeoplePay360 seed data created successfully.")
        )
        # Create the departments used by the demo employees.

    def seed_departments(self):
        departments = {}

        data = [
            ("ENG", "Engineering"),
            ("HR", "Human Resources"),
            ("FIN", "Finance"),
        ]

        for code, name in data:
            department, _ = Department.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": f"{name} department",
                    "is_active": True,
                },
            )

            departments[code] = department

        return departments

    # Create reusable weekly schedules for employees.
    def seed_schedules(self):
        standard, _ = WorkSchedule.objects.update_or_create(
            name="Standard 5 Day",
            defaults={
                "description": "Monday to Friday, 9 AM to 5:30 PM",
                "is_active": True,
            },
        )

        flexible, _ = WorkSchedule.objects.update_or_create(
            name="Flexible 5 Day",
            defaults={
                "description": "Monday to Friday, 10 AM to 6:30 PM",
                "is_active": True,
            },
        )

        # Monday to Friday schedule with a one-hour break.
        for schedule, start_hour in [
            (standard, 9),
            (flexible, 10),
        ]:
            for day in [
                WorkScheduleDay.DayOfWeek.MONDAY,
                WorkScheduleDay.DayOfWeek.TUESDAY,
                WorkScheduleDay.DayOfWeek.WEDNESDAY,
                WorkScheduleDay.DayOfWeek.THURSDAY,
                WorkScheduleDay.DayOfWeek.FRIDAY,
            ]:
                WorkScheduleDay.objects.update_or_create(
                    work_schedule=schedule,
                    day_of_week=day,
                    defaults={
                        "start_time": time(start_hour, 0),
                        "end_time": time(start_hour + 8, 30),
                        "break_minutes": 60,
                    },
                )

        return {
            "standard": standard,
            "flexible": flexible,
        }

    # Create users with different PeoplePay360 roles for RBAC testing.
    def seed_users(self):
        user_data = [
            (
                "aarav",
                "aarav@peoplepay360.com",
                "Aarav",
                "Patel",
                User.Role.EMPLOYEE,
            ),
            (
                "riya",
                "riya@peoplepay360.com",
                "Riya",
                "Shah",
                User.Role.EMPLOYEE,
            ),
            (
                "dev",
                "dev@peoplepay360.com",
                "Dev",
                "Joshi",
                User.Role.EMPLOYEE,
            ),
            (
                "neha",
                "neha@peoplepay360.com",
                "Neha",
                "Mehta",
                User.Role.HR_MANAGER,
            ),
            (
                "karan",
                "karan@peoplepay360.com",
                "Karan",
                "Desai",
                User.Role.HR_PAYROLL_MANAGER,
            ),
        ]

        users = {}

        for username, email, first_name, last_name, role in user_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": role,
                },
            )

            # Set a known development password only when the user is new.
            if created:
                user.set_password("PeoplePay@123")
                user.save()

            users[username] = user

        return users

    # Create employees and connect each one to a Django user.
    def seed_employees(self, departments, schedules, users):
        employee_data = [
            (
                "EMP001",
                "Aarav",
                "Patel",
                "Senior Software Engineer",
                "ENG",
                "standard",
                "FULL_TIME",
                "aarav",
                60000,
            ),
            (
                "EMP002",
                "Riya",
                "Shah",
                "Software Engineer",
                "ENG",
                "standard",
                "FULL_TIME",
                "riya",
                50000,
            ),
            (
                "EMP003",
                "Dev",
                "Joshi",
                "Software Engineer",
                "ENG",
                "flexible",
                "FULL_TIME",
                "dev",
                45000,
            ),
        ]

        employees = {}

        for (
            employee_number,
            first_name,
            last_name,
            job_title,
            department_code,
            schedule_code,
            employee_type,
            username,
            salary,
        ) in employee_data:
            employee, _ = Employee.objects.update_or_create(
                employee_number=employee_number,
                defaults={
                    "user": users[username],
                    "first_name": first_name,
                    "last_name": last_name,
                    "job_title": job_title,
                    "department": departments[department_code],
                    "work_schedule": schedules[schedule_code],
                    "employee_type": employee_type,
                    "status": Employee.Status.ACTIVE,
                    "hire_date": date(2025, 1, 6),
                    "phone": "9876543210",
                    "bank_name": "Demo Bank",
                    "bank_account_number": f"000000{employee_number[-3:]}",
                    "bank_ifsc": "DEMO0001234",
                },
            )

            employees[employee_number] = employee

        return employees

    # Create active contracts that payroll will later use.
    def seed_contracts(self, employees, schedules):
        salary_data = {
            "EMP001": Decimal("60000"),
            "EMP002": Decimal("50000"),
            "EMP003": Decimal("45000"),
        }

        for employee_number, employee in employees.items():
            Contract.objects.update_or_create(
                contract_number=f"CTR-{employee_number}",
                defaults={
                    "employee": employee,
                    "salary_structure": self.get_salary_structure(),
                    "work_schedule": employee.work_schedule,
                    "start_date": date(2025, 1, 6),
                    "end_date": None,
                    "contract_type": Contract.ContractType.PERMANENT,
                    "base_salary": salary_data[employee_number],
                    "currency": "INR",
                    "status": Contract.Status.ACTIVE,
                    "notes": "Demo active employment contract",
                },
            )

    # Create attendance records for a small payroll period.
    def seed_attendance(self, employees, schedules):
        attendance_dates = [
            date(2026, 9, 1),
            date(2026, 9, 2),
            date(2026, 9, 3),
            date(2026, 9, 4),
        ]

        for employee_number, employee in employees.items():
            for attendance_date in attendance_dates:
                status = AttendanceRecord.Status.PRESENT
                check_in = datetime.combine(
                    attendance_date,
                    time(9, 0),
                )
                check_out = datetime.combine(
                    attendance_date,
                    time(17, 30),
                )

                # Add one late record so exception handling can be tested.
                if employee_number == "EMP002" and attendance_date == date(2026, 9, 2):
                    status = AttendanceRecord.Status.LATE
                    check_in = datetime.combine(
                        attendance_date,
                        time(9, 30),
                    )

                # Add one half-day record for testing.
                if employee_number == "EMP003" and attendance_date == date(2026, 9, 3):
                    status = AttendanceRecord.Status.HALF_DAY
                    check_out = datetime.combine(
                        attendance_date,
                        time(13, 0),
                    )

                AttendanceRecord.objects.update_or_create(
                    employee=employee,
                    attendance_date=attendance_date,
                    defaults={
                        "work_schedule": employee.work_schedule,
                        "check_in": check_in,
                        "check_out": check_out,
                        "expected_hours": Decimal("7.5"),
                        "worked_hours": Decimal("0"),
                        "overtime_hours": Decimal("0"),
                        "status": status,
                        "notes": "Demo attendance record",
                    },
                )

    # Create the leave types used by the HR workflow.
    def seed_time_off(self):
        data = [
            (
                "ANNUAL",
                "Annual Leave",
                True,
                True,
            ),
            (
                "SICK",
                "Sick Leave",
                True,
                True,
            ),
            (
                "UNPAID",
                "Unpaid Leave",
                False,
                False,
            ),
            (
                "CASUAL",
                "Casual Leave",
                True,
                True,
            ),
        ]

        for code, name, requires_allocation, is_paid in data:
            TimeOffType.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": f"PeoplePay360 {name.lower()} type",
                    "unit": TimeOffType.Unit.DAYS,
                    "requires_allocation": requires_allocation,
                    "is_paid": is_paid,
                    "is_active": True,
                },
            )

    # Give employees approved leave balances for the current year.
    def seed_allocations(self, employees):
        annual = TimeOffType.objects.get(code="ANNUAL")
        sick = TimeOffType.objects.get(code="SICK")

        for employee in employees.values():
            TimeOffAllocation.objects.update_or_create(
                employee=employee,
                time_off_type=annual,
                allocation_year=2026,
                defaults={
                    "allocated_days": Decimal("20"),
                    "used_days": Decimal("2"),
                    "status": TimeOffAllocation.Status.APPROVED,
                    "valid_from": date(2026, 1, 1),
                    "valid_until": date(2026, 12, 31),
                },
            )

            TimeOffAllocation.objects.update_or_create(
                employee=employee,
                time_off_type=sick,
                allocation_year=2026,
                defaults={
                    "allocated_days": Decimal("12"),
                    "used_days": Decimal("0"),
                    "status": TimeOffAllocation.Status.APPROVED,
                    "valid_from": date(2026, 1, 1),
                    "valid_until": date(2026, 12, 31),
                },
            )

    # Create one salary structure whose rules will later drive payroll.
    def seed_salary_data(self):
        structure, _ = SalaryStructure.objects.update_or_create(
            code="MONTHLY-INR",
            defaults={
                "name": "Monthly Salary - INR",
                "description": "Demo monthly payroll structure",
                "currency": "INR",
                "is_active": True,
            },
        )

        rules = [
            {
                "code": "BASIC",
                "name": "Basic Salary",
                "category": SalaryRule.Category.BASIC,
                "sequence": 10,
                "calculation_type": SalaryRule.CalculationType.FORMULA,
                "formula": "BASE_SALARY",
            },
            {
                "code": "HRA",
                "name": "House Rent Allowance",
                "category": SalaryRule.Category.ALLOWANCE,
                "sequence": 20,
                "calculation_type": SalaryRule.CalculationType.PERCENTAGE,
                "percentage": Decimal("20"),
                "based_on": "BASIC",
            },
            {
                "code": "GROSS",
                "name": "Gross Salary",
                "category": SalaryRule.Category.GROSS,
                "sequence": 30,
                "calculation_type": SalaryRule.CalculationType.FORMULA,
                "formula": "BASIC + HRA",
            },
            {
                "code": "PF",
                "name": "Provident Fund",
                "category": SalaryRule.Category.DEDUCTION,
                "sequence": 40,
                "calculation_type": SalaryRule.CalculationType.PERCENTAGE,
                "percentage": Decimal("12"),
                "based_on": "BASIC",
            },
            {
                "code": "NET",
                "name": "Net Salary",
                "category": SalaryRule.Category.NET,
                "sequence": 50,
                "calculation_type": SalaryRule.CalculationType.FORMULA,
                "formula": "GROSS - PF",
            },
        ]

        for rule_data in rules:
            SalaryRule.objects.update_or_create(
                salary_structure=structure,
                code=rule_data["code"],
                defaults={
                    "name": rule_data["name"],
                    "category": rule_data["category"],
                    "sequence": rule_data["sequence"],
                    "calculation_type": rule_data["calculation_type"],
                    "amount": rule_data.get("amount"),
                    "percentage": rule_data.get("percentage"),
                    "formula": rule_data.get("formula", ""),
                    "based_on": rule_data.get("based_on", ""),
                    "is_active": True,
                },
            )

    # Contracts need the salary structure to exist first.
    def get_salary_structure(self):
        return SalaryStructure.objects.get(
            code="MONTHLY-INR",
        )
