from datetime import date
from decimal import Decimal
from pydantic import BaseModel, model_validator

from app.models.payrun import PayrunStatus


class PayrunCreate(BaseModel):
    period_start: date
    period_end: date
    payment_date: date | None = None

    @model_validator(mode="after")
    def valid_period(self):
        if self.period_end < self.period_start:
            raise ValueError("period_end cannot be before period_start")
        return self


class PayrunResponse(PayrunCreate):
    model_config = {"from_attributes": True}
    id: str
    status: PayrunStatus
    employee_count: int
    total_gross: Decimal
    total_deductions: Decimal
    total_tax: Decimal
    total_net: Decimal
