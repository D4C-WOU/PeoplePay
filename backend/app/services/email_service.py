import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models.employee import Employee
from app.models.payrun import Payrun, PayrunStatus
from app.models.payslip import Payslip, PayslipStatus
from app.services.pdf_service import generate_payslip_pdf

logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_FROM_EMAIL)


def send_email(
    *,
    recipient: str,
    subject: str,
    body: str,
    attachment: bytes | None = None,
    attachment_name: str = "attachment.pdf",
) -> None:
    if not _smtp_configured():
        raise ValueError(
            "SMTP is not configured. Set SMTP_HOST and SMTP_FROM_EMAIL in .env"
        )

    message = EmailMessage()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    if attachment is not None:
        message.add_attachment(
            attachment, maintype="application", subtype="pdf", filename=attachment_name
        )

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
        server.send_message(message)


def send_payrun_payslips(db: Session, payrun: Payrun) -> dict:
    if payrun.status not in {PayrunStatus.COMPLETED, PayrunStatus.PAID}:
        raise ValueError("Only finalized or paid payruns can send payslips")

    slips = list(
        db.scalars(
            select(Payslip).where(
                Payslip.payrun_id == payrun.id,
                Payslip.status.in_([PayslipStatus.FINALIZED, PayslipStatus.PAID]),
            )
        ).all()
    )
    if not slips:
        raise ValueError("Payrun has no finalized or paid payslips")

    sent = []
    failed = []
    for slip in slips:
        employee = db.get(Employee, slip.employee_id)
        if employee is None or not employee.email:
            failed.append(
                {
                    "payslip_id": slip.id,
                    "employee_id": slip.employee_id,
                    "reason": "Missing employee email",
                }
            )
            continue
        try:
            pdf = generate_payslip_pdf(slip)
            send_email(
                recipient=employee.email,
                subject=f"Payslip - {payrun.period_start} to {payrun.period_end}",
                body=f"Hello {slip.employee_name},\n\nPlease find your payslip for {payrun.period_start} to {payrun.period_end} attached.\n\nPeoplePay360",
                attachment=pdf,
                attachment_name=f"payslip-{slip.employee_number}.pdf",
            )
            sent.append(slip.id)
        except Exception as exc:
            logger.exception(
                "Failed to send payslip email", extra={"payslip_id": slip.id}
            )
            failed.append(
                {
                    "payslip_id": slip.id,
                    "employee_id": slip.employee_id,
                    "reason": str(exc),
                }
            )

    return {
        "payrun_id": payrun.id,
        "total": len(slips),
        "sent": len(sent),
        "failed": len(failed),
        "failed_items": failed,
    }
