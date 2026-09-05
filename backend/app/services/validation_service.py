from datetime import date
from decimal import Decimal

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractStatus
from app.models.employee import Employee
from app.models.salary_rule import CalculationType, SalaryRule
from app.models.salary_structure import SalaryStructure


def get_employee(db: Session, employee_id: str) -> Employee:
    employee = db.get(Employee, employee_id)
    if not employee:
        raise ValueError("Employee not found")
    return employee


def validate_contract_dates(start_date: date, end_date: date | None) -> None:
    if end_date and end_date < start_date:
        raise ValueError("Contract end date cannot be before start date")


def validate_contract_dependencies(
    db: Session,
    employee_id: str,
    salary_structure_id: str,
    work_schedule_id: str | None,
) -> None:
    if not db.get(Employee, employee_id):
        raise ValueError("Employee not found")
    if not db.get(SalaryStructure, salary_structure_id):
        raise ValueError("Salary structure not found")
    if work_schedule_id:
        from app.models.work_schedule import WorkSchedule
        if not db.get(WorkSchedule, work_schedule_id):
            raise ValueError("Work schedule not found")


def validate_salary_rule(rule: SalaryRule) -> None:
    if rule.calculation_type == CalculationType.FIXED and rule.amount is None:
        raise ValueError("FIXED rule requires amount")
    if rule.calculation_type == CalculationType.PERCENTAGE:
        if rule.percentage is None or rule.percentage < 0:
            raise ValueError("PERCENTAGE rule requires a valid percentage")
    if rule.calculation_type == CalculationType.FORMULA and not rule.formula:
        raise ValueError("FORMULA rule requires formula")


def ensure_no_overlapping_active_contract(
    db: Session, employee_id: str, start_date: date, end_date: date | None, exclude_id: str | None = None
) -> None:
    stmt = select(Contract).where(
        Contract.employee_id == employee_id,
        Contract.status == ContractStatus.ACTIVE,
    )
    if exclude_id:
        stmt = stmt.where(Contract.id != exclude_id)
    for contract in db.scalars(stmt):
        overlaps = (end_date is None or contract.start_date <= end_date) and (
            contract.end_date is None or contract.end_date >= start_date
        )
        if overlaps:
            raise ValueError("Employee already has an overlapping active contract")
