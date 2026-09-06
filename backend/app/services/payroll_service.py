from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.models.contract import Contract, ContractStatus
from app.models.employee import Employee, EmployeeStatus
from app.models.payrun import Payrun, PayrunStatus
from app.models.payslip import Payslip, PayslipStatus
from app.models.payslip_line import PayslipLine
from app.models.salary_rule import SalaryRule
from app.models.salary_structure import SalaryStructure
from app.schemas.pagination import Page
from app.services.salary_engine import calculate_salary
from app.utils.pagination import paginate_scalars


def create_payrun(
    db: Session,
    period_start: date,
    period_end: date,
    payment_date=None,
    salary_structure_id: str | None = None,
    employee_ids: list[str] | None = None,
) -> Payrun:
    if period_end < period_start:
        raise ValueError("Invalid pay period")
    if salary_structure_id is None:
        raise ValueError("salary_structure_id is required")
    if not employee_ids:
        raise ValueError("At least one employee must be selected")
    employee_ids = list(dict.fromkeys(employee_ids))

    structure = db.get(SalaryStructure, salary_structure_id)
    if structure is None:
        raise ValueError("Salary structure not found")
    if not structure.is_active:
        raise ValueError("Salary structure is inactive")

    existing = db.scalar(
        select(Payrun).where(
            Payrun.period_start == period_start, Payrun.period_end == period_end
        )
    )
    if existing is not None:
        raise ValueError("Payrun for this period already exists")

    employees = list(
        db.scalars(select(Employee).where(Employee.id.in_(employee_ids))).all()
    )
    found = {employee.id for employee in employees}
    missing = [employee_id for employee_id in employee_ids if employee_id not in found]
    if missing:
        raise ValueError(f"Employee(s) not found: {', '.join(missing)}")
    if any(employee.status == EmployeeStatus.TERMINATED for employee in employees):
        raise ValueError("Terminated employees cannot be included in a payrun")

    payrun = Payrun(
        period_start=period_start,
        period_end=period_end,
        payment_date=payment_date,
        salary_structure_id=salary_structure_id,
        selected_employee_ids=employee_ids,
    )
    db.add(payrun)
    try:
        db.commit()
        db.refresh(payrun)
        return payrun
    except Exception:
        db.rollback()
        raise


def list_payruns(
    db: Session,
    status: PayrunStatus | None = None,
    page: int | None = None,
    page_size: int = 10,
) -> list[Payrun] | Page[Payrun]:
    stmt = select(Payrun).order_by(Payrun.period_start.desc())
    if status is not None:
        stmt = stmt.where(Payrun.status == status)
    if page is not None:
        return paginate_scalars(db, stmt, page, page_size)
    return list(db.scalars(stmt).all())


def get_payrun(db: Session, payrun_id: str) -> Payrun:
    payrun = db.get(Payrun, payrun_id)
    if payrun is None:
        raise ValueError("Payrun not found")
    return payrun


def _get_employee_attendance(db, employee_id, period_start, period_end):
    stmt = (
        select(AttendanceRecord)
        .where(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.attendance_date >= period_start,
            AttendanceRecord.attendance_date <= period_end,
        )
        .order_by(AttendanceRecord.attendance_date)
    )
    return list(db.scalars(stmt).all())


def _calculate_worked_days(attendance):
    worked_days = Decimal("0")
    for record in attendance:
        if record.status == AttendanceStatus.PRESENT:
            worked_days += Decimal("1")
        elif record.status == AttendanceStatus.HALF_DAY:
            worked_days += Decimal("0.5")
    return worked_days


def _calculate_overtime_hours(attendance):
    return sum(
        (record.overtime_hours or Decimal("0") for record in attendance), Decimal("0")
    )


def _get_contract(db, employee_id, period_start, period_end):
    return db.scalar(
        select(Contract)
        .options(selectinload(Contract.salary_structure))
        .where(
            Contract.employee_id == employee_id,
            Contract.status == ContractStatus.ACTIVE,
            Contract.start_date <= period_end,
            Contract.end_date.is_(None) | (Contract.end_date >= period_start),
        )
        .order_by(Contract.start_date.desc())
    )


def _recalculate_payrun_totals(db, payrun):
    slips = list(
        db.scalars(select(Payslip).where(Payslip.payrun_id == payrun.id)).all()
    )
    payrun.employee_count = len(slips)
    payrun.total_gross = sum((slip.gross_amount for slip in slips), Decimal("0"))
    payrun.total_deductions = sum(
        (slip.deductions_amount for slip in slips), Decimal("0")
    )
    payrun.total_tax = sum((slip.tax_amount for slip in slips), Decimal("0"))
    payrun.total_net = sum((slip.net_amount for slip in slips), Decimal("0"))


def process_payrun(db: Session, payrun: Payrun) -> Payrun:
    if payrun.status != PayrunStatus.DRAFT:
        raise ValueError("Only DRAFT payruns can be processed")
    if not payrun.salary_structure_id:
        raise ValueError("Payrun has no salary structure")
    if not payrun.selected_employee_ids:
        raise ValueError("Payrun has no selected employees")

    try:
        payrun.status = PayrunStatus.PROCESSING
        db.flush()
        structure = db.get(SalaryStructure, payrun.salary_structure_id)
        if structure is None or not structure.is_active:
            raise ValueError("Selected salary structure is unavailable")

        employees = list(
            db.scalars(
                select(Employee).where(Employee.id.in_(payrun.selected_employee_ids))
            ).all()
        )
        employee_map = {employee.id: employee for employee in employees}
        missing = [
            eid for eid in payrun.selected_employee_ids if eid not in employee_map
        ]
        if missing:
            raise ValueError(f"Selected employee(s) not found: {', '.join(missing)}")

        for employee_id in payrun.selected_employee_ids:
            employee = employee_map[employee_id]
            if employee.status == EmployeeStatus.TERMINATED:
                raise ValueError(f"Employee {employee.employee_number} is terminated")
            contract = _get_contract(
                db, employee.id, payrun.period_start, payrun.period_end
            )
            if contract is None:
                raise ValueError(
                    f"No active contract found for {employee.employee_number} in this pay period"
                )
            if contract.salary_structure_id != payrun.salary_structure_id:
                raise ValueError(
                    f"Employee {employee.employee_number} contract uses a different salary structure"
                )

            existing = db.scalar(
                select(Payslip).where(
                    Payslip.payrun_id == payrun.id, Payslip.employee_id == employee.id
                )
            )
            if existing is not None:
                continue

            rules = list(
                db.scalars(
                    select(SalaryRule)
                    .where(
                        SalaryRule.salary_structure_id == payrun.salary_structure_id,
                        SalaryRule.is_active.is_(True),
                    )
                    .order_by(SalaryRule.sequence, SalaryRule.code)
                ).all()
            )
            if not rules:
                raise ValueError("Selected salary structure has no active salary rules")

            attendance = _get_employee_attendance(
                db, employee.id, payrun.period_start, payrun.period_end
            )
            result = calculate_salary(
                contract.base_salary,
                rules,
                worked_days=_calculate_worked_days(attendance),
                overtime_hours=_calculate_overtime_hours(attendance),
            )

            payslip = Payslip(
                payrun_id=payrun.id,
                employee_id=employee.id,
                contract_id=contract.id,
                employee_number=employee.employee_number,
                employee_name=f"{employee.first_name} {employee.last_name}".strip(),
                currency=contract.currency,
                gross_amount=result["gross"],
                deductions_amount=result["deductions"],
                tax_amount=result["tax"],
                net_amount=result["net"],
                status=PayslipStatus.DRAFT,
            )
            db.add(payslip)
            db.flush()
            for line in result["lines"]:
                db.add(PayslipLine(payslip_id=payslip.id, **line))

        db.flush()
        _recalculate_payrun_totals(db, payrun)
        db.commit()
        db.refresh(payrun)
        return payrun
    except Exception:
        db.rollback()
        raise


def finalize_payrun(db: Session, payrun: Payrun) -> Payrun:
    if payrun.status != PayrunStatus.PROCESSING:
        raise ValueError("Only PROCESSING payruns can be finalized")
    try:
        slips = list(
            db.scalars(select(Payslip).where(Payslip.payrun_id == payrun.id)).all()
        )
        if not slips:
            raise ValueError("Cannot finalize an empty payrun")
        for slip in slips:
            if slip.status != PayslipStatus.DRAFT:
                raise ValueError("Payrun contains a non-draft payslip")
            slip.status = PayslipStatus.FINALIZED
            slip.generated_at = datetime.now(timezone.utc)
        payrun.status = PayrunStatus.COMPLETED
        db.commit()
        db.refresh(payrun)
        return payrun
    except Exception:
        db.rollback()
        raise


def mark_payrun_paid(db: Session, payrun: Payrun) -> Payrun:
    if payrun.status != PayrunStatus.COMPLETED:
        raise ValueError("Only finalized payruns can be marked paid")

    try:
        slips = list(
            db.scalars(select(Payslip).where(Payslip.payrun_id == payrun.id)).all()
        )
        if not slips:
            raise ValueError("Cannot mark an empty payrun as paid")

        for slip in slips:
            if slip.status == PayslipStatus.FINALIZED:
                slip.status = PayslipStatus.PAID
            elif slip.status != PayslipStatus.PAID:
                raise ValueError("Payrun contains a payslip that is not finalized")

        payrun.status = PayrunStatus.PAID
        db.commit()
        db.refresh(payrun)
        return payrun
    except Exception:
        db.rollback()
        raise


def cancel_payrun(db: Session, payrun: Payrun) -> Payrun:
    if payrun.status not in {PayrunStatus.DRAFT, PayrunStatus.PROCESSING}:
        raise ValueError("Only DRAFT or PROCESSING payruns can be cancelled")
    try:
        payrun.status = PayrunStatus.CANCELLED
        db.commit()
        db.refresh(payrun)
        return payrun
    except Exception:
        db.rollback()
        raise
