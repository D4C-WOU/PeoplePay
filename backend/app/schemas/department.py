from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=150)
    code: str = Field(min_length=1, max_length=50)
    description: str | None = None
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    is_active: bool | None = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    description: str | None
    is_active: bool
