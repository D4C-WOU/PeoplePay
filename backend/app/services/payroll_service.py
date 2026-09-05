from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.contract import Contract, ContractStatus
from app.models.employee import Employee, EmployeeStatus
from app.models.payrun import Payrun, PayrunStatus
from app.models.payslip import Payslip, PayslipStatus
from app.models.salary_rule import SalaryRule
from app.services.salary_engine import calculate_salary


def create_payrun(db: Session, period_start: date, period_end: date, payment_date=None) -> Payrun:
    if period_end < period_start:
        raise ValueError("Invalid pay period")
    if db.scalar(select(Payrun).where(Payrun.period_start == period_start, Payrun.period_end == period_end)):
        raise ValueError("Payrun for this period already exists")
    obj = Payrun(period_start=period_start, period_end=period_end, payment_date=payment_date)
    db.add(obj); db.commit(); db.refresh(obj); return obj


def list_payruns(db, status=None):
    stmt = select(Payrun).order_by(Payrun.period_start.desc())
    if status: stmt = stmt.where(Payrun.status == status)
    return db.scalars(stmt).all()


def get_payrun(db, payrun_id):
    obj = db.get(Payrun, payrun_id)
    if not obj: raise ValueError("Payrun not found")
    return obj


def process_payrun(db: Session, payrun: Payrun) -> Payrun:
    if payrun.status != PayrunStatus.DRAFT:
        raise ValueError("Only DRAFT payruns can be processed")
    payrun.status = PayrunStatus.PROCESSING
    db.flush()
    employees = db.scalars(
        select(Employee).where(Employee.status != EmployeeStatus.TERMINATED)
    ).all()
    try:
        for employee in employees:
            contract = db.scalar(
                select(Contract).options(selectinload(Contract.salary_structure)).where(
                    Contract.employee_id == employee.id,
                    Contract.status == ContractStatus.ACTIVE,
                    Contract.start_date <= payrun.period_end,
                    (Contract.end_date.is_(None) | (Contract.end_date >= payrun.period_start)),
                ).order_by(Contract.start_date.desc())
            )
            if not contract:
                continue
            existing = db.scalar(select(Payslip).where(
                Payslip.payrun_id == payrun.id, Payslip.employee_id == employee.id
            ))
            if existing:
                continue
            rules = db.scalars(select(SalaryRule).where(
                SalaryRule.salary_structure_id == contract.salary_structure_id
            ).order_by(SalaryRule.sequence)).all()
            result = calculate_salary(contract.base_salary, rules)
            slip = Payslip(
                payrun_id=payrun.id, employee_id=employee.id, contract_id=contract.id,
                employee_number=employee.employee_number,
                employee_name=f"{employee.first_name} {employee.last_name}".strip(),
                currency=contract.currency, gross_amount=result["gross"],
                deductions_amount=result["deductions"], tax_amount=result["tax"],
                net_amount=result["net"], status=PayslipStatus.DRAFT,
            )
            db.add(slip); db.flush()
            for line in result["lines"]:
                from app.models.payslip_line import PayslipLine
                db.add(PayslipLine(payslip_id=slip.id, **line))
        db.flush()
        slips = db.scalars(select(Payslip).where(Payslip.payrun_id == payrun.id)).all()
        payrun.employee_count = len(slips)
        payrun.total_gross = sum((s.gross_amount for s in slips), Decimal("0"))
        payrun.total_deductions = sum((s.deductions_amount for s in slips), Decimal("0"))
        payrun.total_tax = sum((s.tax_amount for s in slips), Decimal("0"))
        payrun.total_net = sum((s.net_amount for s in slips), Decimal("0"))
        db.commit(); db.refresh(payrun)
        return payrun
    except Exception:
        db.rollback()
        raise


def finalize_payrun(db: Session, payrun: Payrun) -> Payrun:
    if payrun.status != PayrunStatus.PROCESSING:
        raise ValueError("Only PROCESSING payruns can be finalized")
    try:
        slips = db.scalars(select(Payslip).where(Payslip.payrun_id == payrun.id)).all()
        if not slips:
            raise ValueError("Cannot finalize an empty payrun")
        from datetime import datetime, timezone
        for slip in slips:
            if slip.status != PayslipStatus.DRAFT:
                raise ValueError("Payrun contains a non-draft payslip")
            slip.status = PayslipStatus.FINALIZED
            slip.generated_at = datetime.now(timezone.utc)
        payrun.status = PayrunStatus.COMPLETED
        db.commit(); db.refresh(payrun)
        return payrun
    except Exception:
        db.rollback()
        raise


def cancel_payrun(db, payrun):
    if payrun.status not in {PayrunStatus.DRAFT, PayrunStatus.PROCESSING}:
        raise ValueError("Only DRAFT or PROCESSING payruns can be cancelled")
    payrun.status = PayrunStatus.CANCELLED
    db.commit(); db.refresh(payrun); return payrun
