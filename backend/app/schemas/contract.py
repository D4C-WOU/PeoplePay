from datetime import date
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.models.contract import (
    ContractStatus,
    ContractType,
)


class ContractCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    employee_id: str
    salary_structure_id: str
    work_schedule_id: str | None = None
    contract_number: str = Field(
        min_length=1,
        max_length=50,
    )
    start_date: date
    end_date: date | None = None
    contract_type: ContractType = ContractType.FULL_TIME
    base_salary: Decimal = Field(
        ge=0,
    )
    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=10,
    )
    status: ContractStatus = ContractStatus.ACTIVE
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")

        return self


class ContractUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    end_date: date | None = None
    contract_type: ContractType | None = None
    base_salary: Decimal | None = Field(
        default=None,
        ge=0,
    )
    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=10,
    )
    notes: str | None = None


class ContractResponse(ContractCreate):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
