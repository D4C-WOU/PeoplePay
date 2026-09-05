from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.models.payslip import Payslip, PayslipStatus


def _money(value) -> str:
    """
    Format a monetary value consistently for the PDF.
    """

    if value is None:
        return "0.00"

    return f"{value:,.2f}"


def generate_payslip_pdf(
    payslip: Payslip,
) -> bytes:
    """
    Generate a PDF representation of a finalized/paid payslip.

    Payroll calculations are NOT performed here.
    All values are taken from the stored payslip and payslip lines.

    Returns:
        PDF content as bytes.
    """

    if payslip.status not in {
        PayslipStatus.FINALIZED,
        PayslipStatus.PAID,
    }:
        raise ValueError("PDF can only be generated for finalized or paid payslips")

    if payslip.lines is None:
        raise ValueError("Payslip lines are not available")

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Payslip - {payslip.employee_number}",
        author="PeoplePay360",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PayslipTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "PayslipSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        spaceAfter=18,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "NormalText",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
    )

    right_style = ParagraphStyle(
        "RightText",
        parent=normal_style,
        alignment=TA_RIGHT,
    )

    story = []

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "PEOPLEPAY360",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Employee Payslip",
            subtitle_style,
        )
    )

    # --------------------------------------------------------
    # EMPLOYEE INFORMATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Employee Information",
            section_style,
        )
    )

    employee_info = [
        [
            Paragraph("<b>Employee Number</b>", normal_style),
            Paragraph(
                str(payslip.employee_number),
                normal_style,
            ),
            Paragraph("<b>Status</b>", normal_style),
            Paragraph(
                payslip.status.value,
                normal_style,
            ),
        ],
        [
            Paragraph("<b>Employee Name</b>", normal_style),
            Paragraph(
                str(payslip.employee_name),
                normal_style,
            ),
            Paragraph("<b>Currency</b>", normal_style),
            Paragraph(
                str(payslip.currency),
                normal_style,
            ),
        ],
    ]

    employee_table = Table(
        employee_info,
        colWidths=[
            32 * mm,
            55 * mm,
            25 * mm,
            55 * mm,
        ],
    )

    employee_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.whitesmoke,
                ),
                (
                    "BACKGROUND",
                    (2, 0),
                    (2, -1),
                    colors.whitesmoke,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.lightgrey,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(employee_table)
    story.append(Spacer(1, 12))

    # --------------------------------------------------------
    # SALARY BREAKDOWN
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Salary Breakdown",
            section_style,
        )
    )

    line_data = [
        [
            Paragraph("<b>Code</b>", normal_style),
            Paragraph("<b>Description</b>", normal_style),
            Paragraph("<b>Category</b>", normal_style),
            Paragraph("<b>Qty</b>", right_style),
            Paragraph("<b>Rate</b>", right_style),
            Paragraph("<b>Amount</b>", right_style),
        ]
    ]

    for line in sorted(
        payslip.lines,
        key=lambda item: (
            item.sequence,
            item.rule_code,
        ),
    ):
        line_data.append(
            [
                Paragraph(
                    str(line.rule_code),
                    normal_style,
                ),
                Paragraph(
                    str(line.rule_name),
                    normal_style,
                ),
                Paragraph(
                    str(line.category),
                    normal_style,
                ),
                Paragraph(
                    _money(line.quantity),
                    right_style,
                ),
                Paragraph(
                    _money(line.rate),
                    right_style,
                ),
                Paragraph(
                    _money(line.amount),
                    right_style,
                ),
            ]
        )

    if len(line_data) == 1:
        line_data.append(
            [
                Paragraph("-", normal_style),
                Paragraph(
                    "No salary lines",
                    normal_style,
                ),
                Paragraph("-", normal_style),
                Paragraph("-", right_style),
                Paragraph("-", right_style),
                Paragraph("0.00", right_style),
            ]
        )

    salary_table = Table(
        line_data,
        repeatRows=1,
        colWidths=[
            22 * mm,
            42 * mm,
            32 * mm,
            17 * mm,
            25 * mm,
            30 * mm,
        ],
    )

    salary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.black,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(salary_table)
    story.append(Spacer(1, 14))

    # --------------------------------------------------------
    # TOTALS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Payroll Summary",
            section_style,
        )
    )

    totals = [
        [
            Paragraph(
                "<b>Gross Amount</b>",
                normal_style,
            ),
            Paragraph(
                f"{payslip.currency} {_money(payslip.gross_amount)}",
                right_style,
            ),
        ],
        [
            Paragraph(
                "<b>Total Deductions</b>",
                normal_style,
            ),
            Paragraph(
                f"{payslip.currency} {_money(payslip.deductions_amount)}",
                right_style,
            ),
        ],
        [
            Paragraph(
                "<b>Total Tax</b>",
                normal_style,
            ),
            Paragraph(
                f"{payslip.currency} {_money(payslip.tax_amount)}",
                right_style,
            ),
        ],
        [
            Paragraph(
                "<b>Net Pay</b>",
                normal_style,
            ),
            Paragraph(
                f"<b>{payslip.currency} " f"{_money(payslip.net_amount)}</b>",
                right_style,
            ),
        ],
    ]

    totals_table = Table(
        totals,
        colWidths=[
            100 * mm,
            68 * mm,
        ],
        hAlign="RIGHT",
    )

    totals_table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.grey,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.lightgrey,
                ),
                (
                    "BACKGROUND",
                    (0, 3),
                    (-1, 3),
                    colors.whitesmoke,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(totals_table)
    story.append(Spacer(1, 18))

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    generated_text = (
        "This payslip was generated from the finalized payroll "
        "record stored in PeoplePay360."
    )

    if payslip.generated_at:
        generated_text += (
            f" Generated at: " f"{payslip.generated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    story.append(
        Paragraph(
            generated_text,
            subtitle_style,
        )
    )

    document.build(story)

    return buffer.getvalue()
