from pydantic import BaseModel, ConfigDict, Field


class SalaryStructureCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(
        min_length=1,
        max_length=50,
    )

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=10,
    )

    is_active: bool = True


class SalaryStructureUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=10,
    )

    is_active: bool | None = None


class SalaryStructureResponse(SalaryStructureCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
