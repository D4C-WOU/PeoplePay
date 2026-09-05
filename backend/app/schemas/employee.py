from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.employee import EmployeeStatus


class EmployeeBase(BaseModel):
    employee_number: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    date_of_birth: date | None = None
    hire_date: date
    termination_date: date | None = None
    job_title: str | None = Field(default=None, max_length=150)
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    address: str | None = None
    emergency_contact_name: str | None = Field(default=None, max_length=150)
    emergency_contact_phone: str | None = Field(default=None, max_length=30)
    department_id: str | None = None
    user_id: str | None = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    employee_number: str | None = Field(default=None, max_length=50)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    date_of_birth: date | None = None
    hire_date: date | None = None
    termination_date: date | None = None
    job_title: str | None = Field(default=None, max_length=150)
    status: EmployeeStatus | None = None
    address: str | None = None
    emergency_contact_name: str | None = Field(default=None, max_length=150)
    emergency_contact_phone: str | None = Field(default=None, max_length=30)
    department_id: str | None = None
    user_id: str | None = None


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
