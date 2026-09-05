from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.payrun import PayrunStatus


class PayrunCreate(BaseModel):
    period_start: date
    period_end: date
    payment_date: date | None = None
    salary_structure_id: str
    employee_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def valid_period(self):
        if self.period_end < self.period_start:
            raise ValueError("period_end cannot be before period_start")
        if self.payment_date is not None and self.payment_date < self.period_start:
            raise ValueError("payment_date cannot be before period_start")
        if len(set(self.employee_ids)) != len(self.employee_ids):
            raise ValueError("employee_ids cannot contain duplicates")
        return self


class PayrunResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    period_start: date
    period_end: date
    payment_date: date | None
    salary_structure_id: str | None
    employee_ids: list[str] = Field(
        default_factory=list, validation_alias="selected_employee_ids"
    )
    status: PayrunStatus
    employee_count: int
    total_gross: Decimal
    total_deductions: Decimal
    total_tax: Decimal
    total_net: Decimal
