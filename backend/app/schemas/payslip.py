from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.payslip import PayslipStatus


class PayslipLineResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    salary_rule_id: str | None
    rule_code: str
    rule_name: str
    category: str
    quantity: Decimal
    rate: Decimal
    amount: Decimal
    sequence: int


class PayslipResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    payrun_id: str
    employee_id: str
    contract_id: str | None
    employee_number: str
    employee_name: str
    currency: str
    gross_amount: Decimal
    deductions_amount: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    status: PayslipStatus
    generated_at: datetime | None
    lines: list[PayslipLineResponse] = Field(default_factory=list)
