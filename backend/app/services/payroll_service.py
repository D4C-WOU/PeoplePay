from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.attendance import (
    AttendanceRecord,
    AttendanceStatus,
)
from app.models.contract import (
    Contract,
    ContractStatus,
)
from app.models.employee import (
    Employee,
    EmployeeStatus,
)
from app.models.payrun import (
    Payrun,
    PayrunStatus,
)
from app.models.payslip import (
    Payslip,
    PayslipStatus,
)
from app.models.payslip_line import PayslipLine
from app.models.salary_rule import SalaryRule
from app.services.salary_engine import calculate_salary


def create_payrun(
    db: Session,
    period_start: date,
    period_end: date,
    payment_date=None,
) -> Payrun:
    if period_end < period_start:
        raise ValueError("Invalid pay period")

    existing = db.scalar(
        select(Payrun).where(
            Payrun.period_start == period_start,
            Payrun.period_end == period_end,
        )
    )

    if existing is not None:
        raise ValueError("Payrun for this period already exists")

    payrun = Payrun(
        period_start=period_start,
        period_end=period_end,
        payment_date=payment_date,
    )

    db.add(payrun)

    try:
        db.commit()
        db.refresh(payrun)

    except Exception:
        db.rollback()
        raise

    return payrun


def list_payruns(
    db: Session,
    status: PayrunStatus | None = None,
) -> list[Payrun]:
    stmt = select(Payrun).order_by(Payrun.period_start.desc())

    if status is not None:
        stmt = stmt.where(Payrun.status == status)

    return list(db.scalars(stmt).all())


def get_payrun(
    db: Session,
    payrun_id: str,
) -> Payrun:
    payrun = db.get(
        Payrun,
        payrun_id,
    )

    if payrun is None:
        raise ValueError("Payrun not found")

    return payrun


def _get_employee_attendance(
    db: Session,
    employee_id: str,
    period_start: date,
    period_end: date,
) -> list[AttendanceRecord]:
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


def _calculate_worked_days(
    attendance: list[AttendanceRecord],
) -> Decimal:
    """
    Convert attendance records into worked-day
    equivalents for salary formulas.

    PRESENT = 1 day
    HALF_DAY = 0.5 day
    Other statuses = 0 days
    """

    worked_days = Decimal("0")

    for record in attendance:
        if record.status == AttendanceStatus.PRESENT:
            worked_days += Decimal("1")

        elif record.status == AttendanceStatus.HALF_DAY:
            worked_days += Decimal("0.5")

    return worked_days


def _calculate_overtime_hours(
    attendance: list[AttendanceRecord],
) -> Decimal:
    return sum(
        (record.overtime_hours or Decimal("0") for record in attendance),
        Decimal("0"),
    )


def _get_contract(
    db: Session,
    employee_id: str,
    period_start: date,
    period_end: date,
) -> Contract | None:
    return db.scalar(
        select(Contract)
        .options(selectinload(Contract.salary_structure))
        .where(
            Contract.employee_id == employee_id,
            Contract.status == ContractStatus.ACTIVE,
            Contract.start_date <= period_end,
            (Contract.end_date.is_(None) | (Contract.end_date >= period_start)),
        )
        .order_by(Contract.start_date.desc())
    )


def _recalculate_payrun_totals(
    db: Session,
    payrun: Payrun,
) -> None:
    slips = list(
        db.scalars(select(Payslip).where(Payslip.payrun_id == payrun.id)).all()
    )

    payrun.employee_count = len(slips)

    payrun.total_gross = sum(
        (slip.gross_amount for slip in slips),
        Decimal("0"),
    )

    payrun.total_deductions = sum(
        (slip.deductions_amount for slip in slips),
        Decimal("0"),
    )

    payrun.total_tax = sum(
        (slip.tax_amount for slip in slips),
        Decimal("0"),
    )

    payrun.total_net = sum(
        (slip.net_amount for slip in slips),
        Decimal("0"),
    )


def process_payrun(
    db: Session,
    payrun: Payrun,
) -> Payrun:
    if payrun.status != PayrunStatus.DRAFT:
        raise ValueError("Only DRAFT payruns can be processed")

    try:
        payrun.status = PayrunStatus.PROCESSING

        db.flush()

        employees = list(
            db.scalars(
                select(Employee).where(Employee.status != EmployeeStatus.TERMINATED)
            ).all()
        )

        for employee in employees:
            contract = _get_contract(
                db=db,
                employee_id=employee.id,
                period_start=payrun.period_start,
                period_end=payrun.period_end,
            )

            if contract is None:
                continue

            existing = db.scalar(
                select(Payslip).where(
                    Payslip.payrun_id == payrun.id,
                    Payslip.employee_id == employee.id,
                )
            )

            if existing is not None:
                continue

            rules = list(
                db.scalars(
                    select(SalaryRule)
                    .where(
                        SalaryRule.salary_structure_id == contract.salary_structure_id,
                        SalaryRule.is_active.is_(True),
                    )
                    .order_by(
                        SalaryRule.sequence,
                        SalaryRule.code,
                    )
                ).all()
            )

            attendance = _get_employee_attendance(
                db=db,
                employee_id=employee.id,
                period_start=payrun.period_start,
                period_end=payrun.period_end,
            )

            worked_days = _calculate_worked_days(attendance)

            overtime_hours = _calculate_overtime_hours(attendance)

            result = calculate_salary(
                contract.base_salary,
                rules,
                worked_days=worked_days,
                overtime_hours=overtime_hours,
            )

            payslip = Payslip(
                payrun_id=payrun.id,
                employee_id=employee.id,
                contract_id=contract.id,
                employee_number=employee.employee_number,
                employee_name=(
                    f"{employee.first_name} " f"{employee.last_name}"
                ).strip(),
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
                db.add(
                    PayslipLine(
                        payslip_id=payslip.id,
                        **line,
                    )
                )

        db.flush()

        _recalculate_payrun_totals(
            db=db,
            payrun=payrun,
        )

        db.commit()
        db.refresh(payrun)

        return payrun

    except Exception:
        db.rollback()
        raise


def finalize_payrun(
    db: Session,
    payrun: Payrun,
) -> Payrun:
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


def cancel_payrun(
    db: Session,
    payrun: Payrun,
) -> Payrun:
    if payrun.status not in {
        PayrunStatus.DRAFT,
        PayrunStatus.PROCESSING,
    }:
        raise ValueError("Only DRAFT or PROCESSING payruns " "can be cancelled")

    try:
        payrun.status = PayrunStatus.CANCELLED

        db.commit()
        db.refresh(payrun)

        return payrun

    except Exception:
        db.rollback()
        raise
