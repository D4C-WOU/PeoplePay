from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee, EmployeeStatus
from app.models.user import User


def get_employee(
    db: Session,
    employee_id: str,
) -> Employee:
    employee = db.get(
        Employee,
        employee_id,
    )

    if employee is None:
        raise ValueError("Employee not found")

    return employee


def list_employees(
    db: Session,
    department_id: str | None = None,
    status: EmployeeStatus | None = None,
) -> list[Employee]:
    stmt = select(Employee)

    if department_id is not None:
        stmt = stmt.where(Employee.department_id == department_id)

    if status is not None:
        stmt = stmt.where(Employee.status == status)

    stmt = stmt.order_by(Employee.created_at.desc())

    return list(db.scalars(stmt).all())


def create_employee(
    db: Session,
    data: dict,
) -> Employee:
    user_id = data.get("user_id")

    if user_id is not None:
        user = db.get(
            User,
            user_id,
        )

        if user is None:
            raise ValueError("User not found")

        existing_employee = db.scalar(
            select(Employee).where(Employee.user_id == user_id)
        )

        if existing_employee is not None:
            raise ValueError("User is already linked to an employee")

    employee_number = data.get("employee_number")

    if employee_number:
        existing_employee = db.scalar(
            select(Employee).where(Employee.employee_number == employee_number)
        )

        if existing_employee is not None:
            raise ValueError("Employee number already exists")

    email = data.get("email")

    if email:
        existing_email = db.scalar(select(Employee).where(Employee.email == email))

        if existing_email is not None:
            raise ValueError("Employee email already exists")

    employee = Employee(**data)

    db.add(employee)

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise ValueError(
            "Employee could not be created. "
            "Employee number, email, or user may already exist."
        )

    return employee


def update_employee(
    db: Session,
    employee: Employee,
    updates: dict,
) -> Employee:
    new_status = updates.get(
        "status",
        employee.status,
    )

    new_hire_date = updates.get(
        "hire_date",
        employee.hire_date,
    )

    termination_date = updates.get(
        "termination_date",
        employee.termination_date,
    )

    if new_hire_date > date.today():
        raise ValueError("hire_date cannot be in the future")

    if termination_date is not None and termination_date < new_hire_date:
        raise ValueError("termination_date cannot be before hire_date")

    if new_status == EmployeeStatus.TERMINATED and termination_date is None:
        termination_date = date.today()

    if new_status != EmployeeStatus.TERMINATED and termination_date is not None:
        raise ValueError("Termination date can only be set for a terminated employee")

    if "user_id" in updates:
        user_id = updates["user_id"]

        if user_id is not None:
            user = db.get(
                User,
                user_id,
            )

            if user is None:
                raise ValueError("User not found")

            existing_employee = db.scalar(
                select(Employee).where(
                    Employee.user_id == user_id,
                    Employee.id != employee.id,
                )
            )

            if existing_employee is not None:
                raise ValueError("User is already linked to another employee")

    if "employee_number" in updates:
        employee_number = updates["employee_number"]

        if employee_number is not None:
            existing_employee = db.scalar(
                select(Employee).where(
                    Employee.employee_number == employee_number,
                    Employee.id != employee.id,
                )
            )

            if existing_employee is not None:
                raise ValueError("Employee number already exists")

    if "email" in updates:
        email = updates["email"]

        if email is not None:
            existing_email = db.scalar(
                select(Employee).where(
                    Employee.email == email,
                    Employee.id != employee.id,
                )
            )

            if existing_email is not None:
                raise ValueError("Employee email already exists")

    allowed_fields = {
        "employee_number",
        "first_name",
        "last_name",
        "email",
        "phone",
        "date_of_birth",
        "hire_date",
        "termination_date",
        "job_title",
        "status",
        "address",
        "emergency_contact_name",
        "emergency_contact_phone",
        "department_id",
        "user_id",
    }

    for field, value in updates.items():
        if field in allowed_fields:
            setattr(
                employee,
                field,
                value,
            )

    if new_status == EmployeeStatus.TERMINATED:
        employee.termination_date = termination_date

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise ValueError("Employee could not be updated")

    return employee


def terminate_employee(
    db: Session,
    employee: Employee,
) -> Employee:
    if employee.status == EmployeeStatus.TERMINATED:
        return employee

    employee.status = EmployeeStatus.TERMINATED
    employee.termination_date = date.today()

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise ValueError("Employee could not be terminated")

    return employee
