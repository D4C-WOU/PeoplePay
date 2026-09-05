from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.payslip import Payslip, PayslipStatus


def list_payslips(
    db: Session,
    employee_id: str | None = None,
    payrun_id: str | None = None,
    status: PayslipStatus | None = None,
) -> list[Payslip]:
    """
    Return payslips with their lines eagerly loaded.

    Optional filters:
    - employee_id
    - payrun_id
    - status
    """

    stmt = (
        select(Payslip)
        .options(selectinload(Payslip.lines))
        .order_by(Payslip.created_at.desc())
    )

    if employee_id:
        stmt = stmt.where(Payslip.employee_id == employee_id)

    if payrun_id:
        stmt = stmt.where(Payslip.payrun_id == payrun_id)

    if status:
        stmt = stmt.where(Payslip.status == status)

    return db.scalars(stmt).all()


def get_payslip(
    db: Session,
    payslip_id: str,
) -> Payslip:
    """
    Get a single payslip with all payslip lines.
    """

    payslip = db.scalar(
        select(Payslip)
        .options(selectinload(Payslip.lines))
        .where(Payslip.id == payslip_id)
    )

    if payslip is None:
        raise ValueError("Payslip not found")

    return payslip


def mark_paid(
    db: Session,
    payslip: Payslip,
) -> Payslip:
    """
    Mark a finalized payslip as paid.

    Only FINALIZED payslips can become PAID.
    """

    if payslip.status != PayslipStatus.FINALIZED:
        raise ValueError("Only finalized payslips can be marked paid")

    payslip.status = PayslipStatus.PAID

    try:
        db.commit()
        db.refresh(payslip)
        return payslip

    except Exception:
        db.rollback()
        raise
