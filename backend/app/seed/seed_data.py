import os
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password

from app.models.user import User, UserRole

from app.models.department import Department
from app.models.employee import Employee, EmployeeStatus, EmployeeType
from app.models.work_schedule import WorkSchedule
from app.models.work_schedule_day import WorkScheduleDay, DayOfWeek
from app.models.salary_structure import SalaryStructure
from app.models.salary_rule import (
    SalaryRule,
    SalaryRuleCategory,
    CalculationType,
)
from app.models.contract import (
    Contract,
    ContractStatus,
    ContractType,
)
from app.models.attendance import (
    AttendanceRecord,
    AttendanceStatus,
)
from app.models.time_off import (
    TimeOffType,
    TimeOffAllocation,
    TimeOffRequest,
    TimeOffStatus,
)
from app.models.payrun import (
    Payrun,
    PayrunStatus,
)

# ============================================================
# DEMO USERS
# ============================================================

DEMO_USERS = [
    {
        "email": "admin@peoplepay.com",
        "role": UserRole.ADMIN,
        "password_env": "SEED_ADMIN_PASSWORD",
        "default_password": "admin@123",
        "model": User,
    },
    {
        "email": "hr@peoplepay.com",
        "role": UserRole.HR_MANAGER,
        "password_env": "SEED_HR_PASSWORD",
        "default_password": "hr@123",
        "model": User,
    },
    {
        "email": "payroll.manager@peoplepay.com",
        "role": UserRole.PAYROLL_MANAGER,
        "password_env": "SEED_PAYROLL_MANAGER_PASSWORD",
        "default_password": "payrollmanager@123",
        "model": User,
    },
    {
        "email": "employee@peoplepay.com",
        "role": UserRole.EMPLOYEE,
        "password_env": "SEED_EMPLOYEE_PASSWORD",
        "default_password": "employee@123",
        "model": User,
    },
]


# ============================================================
# DEPARTMENTS
# ============================================================

DEPARTMENTS = [
    {
        "name": "Engineering",
        "code": "ENG",
        "description": "Software development and engineering",
    },
    {
        "name": "Human Resources",
        "code": "HR",
        "description": "Employee relations and HR operations",
    },
    {
        "name": "Finance",
        "code": "FIN",
        "description": "Finance, accounting and payroll operations",
    },
    {
        "name": "Sales",
        "code": "SALES",
        "description": "Sales and business development",
    },
    {
        "name": "Operations",
        "code": "OPS",
        "description": "Business operations and administration",
    },
]


# ============================================================
# WORK SCHEDULES
# ============================================================

SCHEDULES = [
    {
        "name": "Standard 5 Day",
        "description": "Monday to Friday, 8 hours per day",
        "monday_hours": Decimal("8"),
        "tuesday_hours": Decimal("8"),
        "wednesday_hours": Decimal("8"),
        "thursday_hours": Decimal("8"),
        "friday_hours": Decimal("8"),
        "saturday_hours": Decimal("0"),
        "sunday_hours": Decimal("0"),
        "expected_daily_hours": Decimal("8"),
        "is_active": True,
        "days": [
            {
                "day_of_week": DayOfWeek.MONDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
            {
                "day_of_week": DayOfWeek.TUESDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
            {
                "day_of_week": DayOfWeek.WEDNESDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
            {
                "day_of_week": DayOfWeek.THURSDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
            {
                "day_of_week": DayOfWeek.FRIDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
        ],
    },
    {
        "name": "Standard 6 Day",
        "description": "Monday to Saturday, 8 hours per day",
        "monday_hours": Decimal("8"),
        "tuesday_hours": Decimal("8"),
        "wednesday_hours": Decimal("8"),
        "thursday_hours": Decimal("8"),
        "friday_hours": Decimal("8"),
        "saturday_hours": Decimal("8"),
        "sunday_hours": Decimal("0"),
        "expected_daily_hours": Decimal("8"),
        "is_active": True,
        "days": [
            {
                "day_of_week": DayOfWeek.MONDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
            {
                "day_of_week": DayOfWeek.TUESDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
            {
                "day_of_week": DayOfWeek.WEDNESDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
            {
                "day_of_week": DayOfWeek.THURSDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
            {
                "day_of_week": DayOfWeek.FRIDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
            {
                "day_of_week": DayOfWeek.SATURDAY,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_minutes": 60,
            },
        ],
    },
]


# ============================================================
# SALARY STRUCTURE
# ============================================================

SALARY_STRUCTURES = [
    {
        "code": "MONTHLY",
        "name": "Monthly Salary",
        "description": "Standard monthly employee salary structure",
        "currency": "INR",
        "is_active": True,
    },
]


SALARY_RULES = [
    {
        "code": "BASIC",
        "name": "Basic Salary",
        "category": SalaryRuleCategory.EARNING,
        "calculation_type": CalculationType.PERCENTAGE,
        "amount": None,
        "percentage": Decimal("50"),
        "based_on": "base_salary",
        "formula": None,
        "sequence": 10,
        "is_active": True,
    },
    {
        "code": "HRA",
        "name": "House Rent Allowance",
        "category": SalaryRuleCategory.EARNING,
        "calculation_type": CalculationType.PERCENTAGE,
        "amount": None,
        "percentage": Decimal("20"),
        "based_on": "BASIC",
        "formula": None,
        "sequence": 20,
        "is_active": True,
    },
    {
        "code": "ALLOWANCE",
        "name": "Special Allowance",
        "category": SalaryRuleCategory.EARNING,
        "calculation_type": CalculationType.FIXED,
        "amount": Decimal("5000"),
        "percentage": None,
        "based_on": None,
        "formula": None,
        "sequence": 30,
        "is_active": True,
    },
    {
        "code": "PF",
        "name": "Provident Fund",
        "category": SalaryRuleCategory.DEDUCTION,
        "calculation_type": CalculationType.PERCENTAGE,
        "amount": None,
        "percentage": Decimal("12"),
        "based_on": "gross",
        "formula": None,
        "sequence": 40,
        "is_active": True,
    },
    {
        "code": "TAX",
        "name": "Income Tax",
        "category": SalaryRuleCategory.TAX,
        "calculation_type": CalculationType.PERCENTAGE,
        "amount": None,
        "percentage": Decimal("5"),
        "based_on": "gross",
        "formula": None,
        "sequence": 50,
        "is_active": True,
    },
]


# ============================================================
# EMPLOYEES
# ============================================================

EMPLOYEES = [
    {
        "employee_number": "EMP001",
        "first_name": "Nand",
        "last_name": "Joshi",
        "email": "employee@peoplepay.com",
        "phone": "+91-9000000001",
        "date_of_birth": date(2003, 1, 15),
        "hire_date": date(2025, 7, 1),
        "termination_date": None,
        "job_title": "Software Engineer",
        "status": EmployeeStatus.ACTIVE,
        "address": "Ahmedabad, Gujarat",
        "emergency_contact_name": "Demo Contact",
        "emergency_contact_phone": "+91-9000000011",
        "department_code": "ENG",
        "user_email": "employee@peoplepay.com",
    },
    {
        "employee_number": "EMP002",
        "first_name": "Aarav",
        "last_name": "Shah",
        "email": "aarav@peoplepay.com",
        "phone": "+91-9000000002",
        "date_of_birth": date(2002, 5, 20),
        "hire_date": date(2024, 8, 1),
        "termination_date": None,
        "job_title": "Senior Software Engineer",
        "status": EmployeeStatus.ACTIVE,
        "address": "Ahmedabad, Gujarat",
        "emergency_contact_name": "Demo Contact",
        "emergency_contact_phone": "+91-9000000012",
        "department_code": "ENG",
        "user_email": None,
    },
    {
        "employee_number": "EMP003",
        "first_name": "Priya",
        "last_name": "Patel",
        "email": "priya@peoplepay.com",
        "phone": "+91-9000000003",
        "date_of_birth": date(2001, 9, 10),
        "hire_date": date(2024, 6, 15),
        "termination_date": None,
        "job_title": "HR Executive",
        "status": EmployeeStatus.ACTIVE,
        "address": "Ahmedabad, Gujarat",
        "emergency_contact_name": "Demo Contact",
        "emergency_contact_phone": "+91-9000000013",
        "department_code": "HR",
        "user_email": None,
    },
    {
        "employee_number": "EMP004",
        "first_name": "Rahul",
        "last_name": "Mehta",
        "email": "rahul@peoplepay.com",
        "phone": "+91-9000000004",
        "date_of_birth": date(2000, 11, 5),
        "hire_date": date(2023, 4, 10),
        "termination_date": None,
        "job_title": "Finance Analyst",
        "status": EmployeeStatus.ACTIVE,
        "address": "Ahmedabad, Gujarat",
        "emergency_contact_name": "Demo Contact",
        "emergency_contact_phone": "+91-9000000014",
        "department_code": "FIN",
        "user_email": None,
    },
    {
        "employee_number": "EMP005",
        "first_name": "Neha",
        "last_name": "Desai",
        "email": "neha@peoplepay.com",
        "phone": "+91-9000000005",
        "date_of_birth": date(2002, 3, 18),
        "hire_date": date(2024, 1, 8),
        "termination_date": None,
        "job_title": "Sales Executive",
        "status": EmployeeStatus.ACTIVE,
        "address": "Ahmedabad, Gujarat",
        "emergency_contact_name": "Demo Contact",
        "emergency_contact_phone": "+91-9000000015",
        "department_code": "SALES",
        "user_email": None,
    },
]


# ============================================================
# TIME OFF TYPES
# ============================================================

TIME_OFF_TYPES = [
    {
        "code": "ANNUAL",
        "name": "Annual Leave",
        "description": "Paid annual vacation leave",
        "default_allocation": Decimal("20"),
        "is_paid": True,
        "is_active": True,
    },
    {
        "code": "SICK",
        "name": "Sick Leave",
        "description": "Leave due to illness",
        "default_allocation": Decimal("10"),
        "is_paid": True,
        "is_active": True,
    },
    {
        "code": "UNPAID",
        "name": "Unpaid Leave",
        "description": "Unpaid time off",
        "default_allocation": Decimal("0"),
        "is_paid": False,
        "is_active": True,
    },
]


# ============================================================
# HELPERS
# ============================================================


def get_by_code(
    db: Session,
    model,
    code: str,
):
    return db.scalar(select(model).where(model.code == code))


def get_by_email(
    db: Session,
    email: str,
):
    return db.scalar(select(User).where(User.email == email))


# ============================================================
# USERS
# ============================================================


def seed_users(db: Session) -> None:

    for user_data in DEMO_USERS:

        existing = get_by_email(
            db,
            user_data["email"],
        )

        if existing:
            continue

        password = os.getenv(
            user_data["password_env"],
            user_data["default_password"],
        )

        user = user_data["model"](
            email=user_data["email"],
            role=user_data["role"],
            password_hash=hash_password(password),
            is_active=True,
        )

        db.add(user)

    db.commit()


# ============================================================
# DEPARTMENTS
# ============================================================


def seed_departments(db: Session) -> None:

    for data in DEPARTMENTS:

        existing = get_by_code(
            db,
            Department,
            data["code"],
        )

        if existing:
            continue

        department = Department(
            **data,
            is_active=True,
        )

        db.add(department)

    db.commit()


# ============================================================
# SCHEDULES
# ============================================================


def seed_schedules(db: Session) -> None:

    for data in SCHEDULES:

        existing = db.scalar(
            select(WorkSchedule).where(WorkSchedule.name == data["name"])
        )

        if existing:
            continue

        schedule_data = dict(data)
        days = schedule_data.pop("days", [])
        schedule = WorkSchedule(**schedule_data)
        for day in days:
            schedule.days.append(WorkScheduleDay(**day))
        db.add(schedule)

    db.commit()


# ============================================================
# SALARY STRUCTURES + RULES
# ============================================================


def seed_salary_data(db: Session) -> None:

    for data in SALARY_STRUCTURES:

        existing = get_by_code(
            db,
            SalaryStructure,
            data["code"],
        )

        if existing:
            continue

        db.add(SalaryStructure(**data))

    db.commit()

    monthly = get_by_code(
        db,
        SalaryStructure,
        "MONTHLY",
    )

    if monthly is None:
        raise RuntimeError("MONTHLY salary structure could not be created")

    for data in SALARY_RULES:

        existing = db.scalar(
            select(SalaryRule).where(
                SalaryRule.salary_structure_id == monthly.id,
                SalaryRule.code == data["code"],
            )
        )

        if existing:
            continue

        db.add(
            SalaryRule(
                salary_structure_id=monthly.id,
                **data,
            )
        )

    db.commit()


# ============================================================
# EMPLOYEES
# ============================================================


def seed_employees(db: Session) -> None:

    monthly = get_by_code(
        db,
        SalaryStructure,
        "MONTHLY",
    )

    standard_schedule = db.scalar(
        select(WorkSchedule).where(WorkSchedule.name == "Standard 5 Day")
    )

    if monthly is None or standard_schedule is None:
        raise RuntimeError("Salary structure or schedule missing")

    for data in EMPLOYEES:

        existing = db.scalar(
            select(Employee).where(Employee.employee_number == data["employee_number"])
        )

        if existing:
            continue

        department = get_by_code(
            db,
            Department,
            data["department_code"],
        )

        if department is None:
            raise RuntimeError(f"Department {data['department_code']} not found")

        user = None

        if data["user_email"]:
            user = get_by_email(
                db,
                data["user_email"],
            )

        employee = Employee(
            employee_number=data["employee_number"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data["phone"],
            employee_type=data.get("employee_type", EmployeeType.FULL_TIME),
            bank_name=data.get("bank_name", "PeoplePay Demo Bank"),
            bank_account_number=data.get(
                "bank_account_number", f"DEMO{data['employee_number'][-3:]}"
            ),
            bank_ifsc=data.get("bank_ifsc", "PEOP0000001"),
            manager_id=data.get("manager_id"),
            date_of_birth=data["date_of_birth"],
            hire_date=data["hire_date"],
            termination_date=data["termination_date"],
            job_title=data["job_title"],
            status=data["status"],
            address=data["address"],
            emergency_contact_name=data["emergency_contact_name"],
            emergency_contact_phone=data["emergency_contact_phone"],
            department_id=department.id,
            user_id=user.id if user else None,
        )

        db.add(employee)

    db.commit()


# ============================================================
# CONTRACTS
# ============================================================


def seed_contracts(db: Session) -> None:

    monthly = get_by_code(
        db,
        SalaryStructure,
        "MONTHLY",
    )

    schedule = db.scalar(
        select(WorkSchedule).where(WorkSchedule.name == "Standard 5 Day")
    )

    if monthly is None or schedule is None:
        raise RuntimeError("Salary structure or schedule missing")

    salaries = {
        "EMP001": Decimal("60000"),
        "EMP002": Decimal("80000"),
        "EMP003": Decimal("45000"),
        "EMP004": Decimal("55000"),
        "EMP005": Decimal("50000"),
    }

    employees = db.scalars(select(Employee)).all()

    for employee in employees:

        if employee.employee_number not in salaries:
            continue

        existing = db.scalar(
            select(Contract).where(Contract.employee_id == employee.id)
        )

        if existing:
            continue

        contract = Contract(
            employee_id=employee.id,
            salary_structure_id=monthly.id,
            work_schedule_id=schedule.id,
            contract_number=(f"CTR-{employee.employee_number}"),
            start_date=employee.hire_date,
            end_date=None,
            contract_type=ContractType.FULL_TIME,
            base_salary=salaries[employee.employee_number],
            currency="INR",
            status=ContractStatus.ACTIVE,
            notes="Demo active employment contract",
        )

        db.add(contract)

    db.commit()


# ============================================================
# ATTENDANCE
# ============================================================


def seed_attendance(db: Session) -> None:

    schedule = db.scalar(
        select(WorkSchedule).where(WorkSchedule.name == "Standard 5 Day")
    )

    if schedule is None:
        raise RuntimeError("Standard 5 Day schedule missing")

    employees = db.scalars(
        select(Employee).where(Employee.status == EmployeeStatus.ACTIVE)
    ).all()

    demo_dates = [
        date(2026, 8, 31),
        date(2026, 9, 1),
        date(2026, 9, 2),
        date(2026, 9, 3),
        date(2026, 9, 4),
    ]

    for employee in employees:

        for attendance_date in demo_dates:

            existing = db.scalar(
                select(AttendanceRecord).where(
                    AttendanceRecord.employee_id == employee.id,
                    AttendanceRecord.attendance_date == attendance_date,
                )
            )

            if existing:
                continue

            check_in = time(9, 0)
            check_out = time(17, 30)

            status = AttendanceStatus.PRESENT

            # One late record for demo/testing
            if employee.employee_number == "EMP002" and attendance_date == date(
                2026, 9, 2
            ):
                check_in = time(9, 30)
                status = AttendanceStatus.LATE

            # One half day for demo/testing
            if employee.employee_number == "EMP003" and attendance_date == date(
                2026, 9, 3
            ):
                check_in = time(9, 0)
                check_out = time(13, 0)
                status = AttendanceStatus.HALF_DAY

            db.add(
                AttendanceRecord(
                    employee_id=employee.id,
                    work_schedule_id=schedule.id,
                    attendance_date=attendance_date,
                    check_in=check_in,
                    check_out=check_out,
                    expected_hours=Decimal("8"),
                    status=status,
                    notes="Demo attendance record",
                )
            )

    db.commit()


# ============================================================
# TIME OFF TYPES
# ============================================================


def seed_time_off_types(db: Session) -> None:

    for data in TIME_OFF_TYPES:

        existing = get_by_code(
            db,
            TimeOffType,
            data["code"],
        )

        if existing:
            continue

        db.add(TimeOffType(**data))

    db.commit()


# ============================================================
# TIME OFF ALLOCATIONS
# ============================================================


def seed_time_off_allocations(
    db: Session,
) -> None:

    annual = get_by_code(
        db,
        TimeOffType,
        "ANNUAL",
    )

    sick = get_by_code(
        db,
        TimeOffType,
        "SICK",
    )

    if annual is None or sick is None:
        raise RuntimeError("Time-off types missing")

    employees = db.scalars(
        select(Employee).where(Employee.status == EmployeeStatus.ACTIVE)
    ).all()

    for employee in employees:

        for time_off_type, days in [
            (annual, Decimal("20")),
            (sick, Decimal("10")),
        ]:

            existing = db.scalar(
                select(TimeOffAllocation).where(
                    TimeOffAllocation.employee_id == employee.id,
                    TimeOffAllocation.time_off_type_id == time_off_type.id,
                    TimeOffAllocation.year == 2026,
                )
            )

            if existing:
                continue

            db.add(
                TimeOffAllocation(
                    employee_id=employee.id,
                    time_off_type_id=time_off_type.id,
                    year=2026,
                    allocated_days=days,
                    used_days=Decimal("0"),
                )
            )

    db.commit()


# ============================================================
# TIME OFF REQUESTS
# ============================================================


def seed_time_off_requests(
    db: Session,
) -> None:

    annual = get_by_code(
        db,
        TimeOffType,
        "ANNUAL",
    )

    if annual is None:
        raise RuntimeError("Annual leave type missing")

    employee = db.scalar(select(Employee).where(Employee.employee_number == "EMP001"))

    if employee is None:
        raise RuntimeError("EMP001 missing")

    existing = db.scalar(
        select(TimeOffRequest).where(
            TimeOffRequest.employee_id == employee.id,
            TimeOffRequest.time_off_type_id == annual.id,
            TimeOffRequest.start_date == date(2026, 9, 14),
        )
    )

    if existing:
        return

    db.add(
        TimeOffRequest(
            employee_id=employee.id,
            time_off_type_id=annual.id,
            start_date=date(2026, 9, 14),
            end_date=date(2026, 9, 16),
            requested_days=Decimal("3"),
            reason="Family vacation",
            status=TimeOffStatus.PENDING,
        )
    )

    db.commit()


# ============================================================
# PAYRUN
# ============================================================


def seed_payrun(db: Session) -> None:
    existing = db.scalar(
        select(Payrun).where(
            Payrun.period_start == date(2026, 8, 1),
            Payrun.period_end == date(2026, 8, 31),
        )
    )
    if existing:
        return

    monthly = get_by_code(db, SalaryStructure, "MONTHLY")
    if monthly is None:
        raise RuntimeError("MONTHLY salary structure missing")

    employees = list(
        db.scalars(
            select(Employee).where(Employee.status == EmployeeStatus.ACTIVE)
        ).all()
    )
    payrun = Payrun(
        period_start=date(2026, 8, 1),
        period_end=date(2026, 8, 31),
        payment_date=date(2026, 9, 5),
        salary_structure_id=monthly.id,
        selected_employee_ids=[employee.id for employee in employees],
        status=PayrunStatus.DRAFT,
    )
    db.add(payrun)
    db.commit()


# ============================================================
# MAIN SEED
# ============================================================


def seed(db: Session) -> None:

    print("Seeding users...")
    seed_users(db)

    print("Seeding departments...")
    seed_departments(db)

    print("Seeding work schedules...")
    seed_schedules(db)

    print("Seeding salary structures and rules...")
    seed_salary_data(db)

    print("Seeding employees...")
    seed_employees(db)

    print("Seeding contracts...")
    seed_contracts(db)

    print("Seeding attendance...")
    seed_attendance(db)

    print("Seeding time-off types...")
    seed_time_off_types(db)

    print("Seeding time-off allocations...")
    seed_time_off_allocations(db)

    print("Seeding time-off requests...")
    seed_time_off_requests(db)

    print("Seeding draft payrun...")
    seed_payrun(db)

    print("Seed completed successfully.")


if __name__ == "__main__":

    from app.db.database import SessionLocal

    db = SessionLocal()

    try:
        seed(db)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
