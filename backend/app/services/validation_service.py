from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractStatus
from app.models.employee import Employee
from app.models.salary_rule import CalculationType, SalaryRule
from app.models.salary_structure import SalaryStructure


def get_employee(
    db: Session,
    employee_id: str,
) -> Employee:
    employee = db.get(
        Employee,
        employee_id,
    )

    if not employee:
        raise ValueError("Employee not found")

    return employee


def validate_contract_dates(
    start_date: date,
    end_date: date | None,
) -> None:
    if end_date is not None and end_date < start_date:
        raise ValueError("Contract end date cannot be before start date")


def validate_contract_dependencies(
    db: Session,
    employee_id: str,
    salary_structure_id: str,
    work_schedule_id: str | None,
) -> None:
    employee = db.get(
        Employee,
        employee_id,
    )

    if not employee:
        raise ValueError("Employee not found")

    salary_structure = db.get(
        SalaryStructure,
        salary_structure_id,
    )

    if not salary_structure:
        raise ValueError("Salary structure not found")

    if not salary_structure.is_active:
        raise ValueError("Salary structure is inactive")

    if work_schedule_id:
        from app.models.work_schedule import WorkSchedule

        work_schedule = db.get(
            WorkSchedule,
            work_schedule_id,
        )

        if not work_schedule:
            raise ValueError("Work schedule not found")

        if not work_schedule.is_active:
            raise ValueError("Work schedule is inactive")


def validate_salary_rule(
    rule: SalaryRule,
) -> None:
    if not rule.code or not rule.code.strip():
        raise ValueError("Salary rule code cannot be empty")

    if not rule.name or not rule.name.strip():
        raise ValueError("Salary rule name cannot be empty")

    if rule.sequence < 1:
        raise ValueError("Salary rule sequence must be at least 1")

    if rule.calculation_type == CalculationType.FIXED:
        if rule.amount is None:
            raise ValueError("FIXED rule requires amount")

    elif rule.calculation_type == CalculationType.PERCENTAGE:
        if rule.percentage is None:
            raise ValueError("PERCENTAGE rule requires percentage")

        if rule.percentage < 0:
            raise ValueError("PERCENTAGE rule requires a valid percentage")

    elif rule.calculation_type == CalculationType.FORMULA:
        if not rule.formula or not rule.formula.strip():
            raise ValueError("FORMULA rule requires formula")

    else:
        raise ValueError("Unsupported salary rule calculation type")


def ensure_no_overlapping_active_contract(
    db: Session,
    employee_id: str,
    start_date: date,
    end_date: date | None,
    exclude_id: str | None = None,
) -> None:
    stmt = select(Contract).where(
        Contract.employee_id == employee_id,
        Contract.status == ContractStatus.ACTIVE,
    )

    if exclude_id:
        stmt = stmt.where(Contract.id != exclude_id)

    contracts = db.scalars(stmt).all()

    for contract in contracts:
        overlaps = (end_date is None or contract.start_date <= end_date) and (
            contract.end_date is None or contract.end_date >= start_date
        )

        if overlaps:
            raise ValueError("Employee already has an overlapping active contract")


def validate_payrun(db: Session, payrun) -> dict:
    from app.models.attendance import AttendanceRecord, AttendanceStatus
    from app.models.payslip import Payslip

    warnings = []
    employee_ids = payrun.selected_employee_ids or []
    employees = (
        list(db.scalars(select(Employee).where(Employee.id.in_(employee_ids))).all())
        if employee_ids
        else []
    )
    for employee in employees:
        missing_bank = (
            not employee.bank_name
            or not employee.bank_account_number
            or not employee.bank_ifsc
        )
        if missing_bank:
            warnings.append(
                {
                    "employee_id": employee.id,
                    "employee_number": employee.employee_number,
                    "type": "MISSING_BANK_DETAILS",
                    "message": "Bank details are incomplete.",
                }
            )
        contract = db.scalar(
            select(Contract)
            .where(
                Contract.employee_id == employee.id,
                Contract.status == ContractStatus.ACTIVE,
                Contract.start_date <= payrun.period_end,
                Contract.end_date.is_(None)
                | (Contract.end_date >= payrun.period_start),
            )
            .order_by(Contract.start_date.desc())
        )
        if contract is None:
            warnings.append(
                {
                    "employee_id": employee.id,
                    "employee_number": employee.employee_number,
                    "type": "MISSING_CONTRACT",
                    "message": "No active contract covers the payrun period.",
                }
            )
        elif (
            payrun.salary_structure_id
            and contract.salary_structure_id != payrun.salary_structure_id
        ):
            warnings.append(
                {
                    "employee_id": employee.id,
                    "employee_number": employee.employee_number,
                    "type": "SALARY_STRUCTURE_MISMATCH",
                    "message": "Employee contract uses a different salary structure.",
                }
            )

    return {
        "payrun_id": payrun.id,
        "valid": not warnings,
        "warning_count": len(warnings),
        "warnings": warnings,
    }
