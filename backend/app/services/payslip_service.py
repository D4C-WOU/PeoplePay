from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.payslip import Payslip, PayslipStatus


def list_payslips(db, employee_id=None, payrun_id=None, status=None):
    stmt = select(Payslip).options(selectinload(Payslip.lines)).order_by(Payslip.created_at.desc())
    if employee_id: stmt = stmt.where(Payslip.employee_id == employee_id)
    if payrun_id: stmt = stmt.where(Payslip.payrun_id == payrun_id)
    if status: stmt = stmt.where(Payslip.status == status)
    return db.scalars(stmt).all()


def get_payslip(db: Session, payslip_id: str) -> Payslip:
    obj = db.scalar(select(Payslip).options(selectinload(Payslip.lines)).where(Payslip.id == payslip_id))
    if not obj: raise ValueError("Payslip not found")
    return obj


def mark_paid(db, payslip):
    if payslip.status != PayslipStatus.FINALIZED:
        raise ValueError("Only finalized payslips can be marked paid")
    payslip.status = PayslipStatus.PAID
    db.commit(); db.refresh(payslip); return payslip
