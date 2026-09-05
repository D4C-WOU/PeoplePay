from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.salary_rule import CalculationType, SalaryRuleCategory


class SalaryRuleCreate(BaseModel):
    salary_structure_id: str
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    category: SalaryRuleCategory
    calculation_type: CalculationType = CalculationType.FIXED
    amount: Decimal | None = Field(default=None, ge=0)
    percentage: Decimal | None = Field(default=None, ge=0)
    formula: str | None = None
    sequence: int = Field(default=1, ge=1)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_calculation(self):
        if self.calculation_type == CalculationType.FIXED and self.amount is None:
            raise ValueError("FIXED rules require amount")
        if self.calculation_type == CalculationType.PERCENTAGE and self.percentage is None:
            raise ValueError("PERCENTAGE rules require percentage")
        if self.calculation_type == CalculationType.FORMULA and not self.formula:
            raise ValueError("FORMULA rules require formula")
        return self


class SalaryRuleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    category: SalaryRuleCategory | None = None
    calculation_type: CalculationType | None = None
    amount: Decimal | None = Field(default=None, ge=0)
    percentage: Decimal | None = Field(default=None, ge=0)
    formula: str | None = None
    sequence: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class SalaryRuleResponse(SalaryRuleCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
