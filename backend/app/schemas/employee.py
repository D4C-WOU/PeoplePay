from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator,
)

from app.models.employee import EmployeeStatus


class EmployeeBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    employee_number: str = Field(
        min_length=1,
        max_length=50,
    )
    first_name: str = Field(
        min_length=1,
        max_length=100,
    )
    last_name: str = Field(
        min_length=1,
        max_length=100,
    )
    email: EmailStr
    phone: str | None = Field(
        default=None,
        max_length=30,
    )
    date_of_birth: date | None = None
    hire_date: date
    termination_date: date | None = None
    job_title: str | None = Field(
        default=None,
        max_length=150,
    )
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    address: str | None = None
    emergency_contact_name: str | None = Field(
        default=None,
        max_length=150,
    )
    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )
    department_id: str | None = None
    user_id: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.hire_date > date.today():
            raise ValueError("hire_date cannot be in the future")

        if self.termination_date is not None and self.termination_date < self.hire_date:
            raise ValueError("termination_date cannot be before hire_date")

        if self.status == EmployeeStatus.TERMINATED and self.termination_date is None:
            raise ValueError("termination_date is required for a terminated employee")

        if (
            self.status != EmployeeStatus.TERMINATED
            and self.termination_date is not None
        ):
            raise ValueError(
                "termination_date can only be set for a terminated employee"
            )

        return self


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    employee_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        max_length=30,
    )
    date_of_birth: date | None = None
    hire_date: date | None = None
    termination_date: date | None = None
    job_title: str | None = Field(
        default=None,
        max_length=150,
    )
    status: EmployeeStatus | None = None
    address: str | None = None
    emergency_contact_name: str | None = Field(
        default=None,
        max_length=150,
    )
    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )
    department_id: str | None = None
    user_id: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.hire_date is not None and self.hire_date > date.today():
            raise ValueError("hire_date cannot be in the future")

        if (
            self.hire_date is not None
            and self.termination_date is not None
            and self.termination_date < self.hire_date
        ):
            raise ValueError("termination_date cannot be before hire_date")

        return self


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
