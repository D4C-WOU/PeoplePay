from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_payslip_pdf(payslip) -> BytesIO:
    if payslip.status.value not in {"FINALIZED", "PAID"}:
        raise ValueError("Only finalized or paid payslips can generate a PDF")
    buf = BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    _, height = A4
    pdf.setTitle(f"Payslip-{payslip.employee_number}")
    pdf.drawString(50, height - 60, "PeoplePay — Payslip")
    pdf.drawString(50, height - 90, f"Employee: {payslip.employee_name} ({payslip.employee_number})")
    y = height - 130
    for label, value in [
        ("Gross", payslip.gross_amount), ("Deductions", payslip.deductions_amount),
        ("Tax", payslip.tax_amount), ("Net", payslip.net_amount)
    ]:
        pdf.drawString(70, y, f"{label}: {value} {payslip.currency}"); y -= 22
    y -= 10
    pdf.drawString(50, y, "Lines"); y -= 22
    for line in sorted(payslip.lines, key=lambda x: x.sequence):
        pdf.drawString(60, y, f"{line.rule_code} — {line.rule_name}: {line.amount}"); y -= 18
        if y < 60:
            pdf.showPage(); y = height - 60
    pdf.save(); buf.seek(0); return buf
