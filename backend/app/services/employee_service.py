from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.employee import Employee, EmployeeStatus
from app.models.user import User, UserRole


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

    stmt = select(Employee).order_by(Employee.created_at.desc())

    if department_id is not None:
        stmt = stmt.where(Employee.department_id == department_id)

    if status is not None:
        stmt = stmt.where(Employee.status == status)

    return list(db.scalars(stmt).all())


def _validate_user_for_employee(
    db: Session,
    user_id: str,
    exclude_employee_id: str | None = None,
) -> User:

    user = db.get(
        User,
        user_id,
    )

    if user is None:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("Employee user account must be active")

    if user.role != UserRole.EMPLOYEE:
        raise ValueError("Linked user must have the EMPLOYEE role")

    stmt = select(Employee).where(Employee.user_id == user_id)

    if exclude_employee_id is not None:
        stmt = stmt.where(Employee.id != exclude_employee_id)

    existing_employee = db.scalar(stmt)

    if existing_employee is not None:
        raise ValueError("User is already linked to another employee")

    return user


def create_employee(
    db: Session,
    data: dict,
) -> Employee:

    user_id = data.get("user_id")

    if user_id is not None:
        _validate_user_for_employee(
            db,
            user_id,
        )

    employee_number = data.get("employee_number")

    if employee_number:
        existing = db.scalar(
            select(Employee).where(Employee.employee_number == employee_number)
        )

        if existing is not None:
            raise ValueError("Employee number already exists")

    email = data.get("email")

    if email:
        existing = db.scalar(select(Employee).where(Employee.email == email))

        if existing is not None:
            raise ValueError("Employee email already exists")

    employee = Employee(**data)

    db.add(employee)

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise ValueError(
            "Employee could not be created because of a duplicate or invalid reference"
        )

    return employee


def update_employee(
    db: Session,
    employee_id: str,
    data: dict,
) -> Employee:

    employee = get_employee(
        db,
        employee_id,
    )

    updates = dict(data)

    new_user_id = updates.get("user_id")

    if new_user_id is not None and new_user_id != employee.user_id:
        _validate_user_for_employee(
            db,
            new_user_id,
            exclude_employee_id=employee.id,
        )

    if (
        "employee_number" in updates
        and updates["employee_number"] != employee.employee_number
    ):
        existing = db.scalar(
            select(Employee).where(
                Employee.employee_number == updates["employee_number"],
                Employee.id != employee.id,
            )
        )

        if existing is not None:
            raise ValueError("Employee number already exists")

    if "email" in updates and updates["email"] != employee.email:
        existing = db.scalar(
            select(Employee).where(
                Employee.email == updates["email"],
                Employee.id != employee.id,
            )
        )

        if existing is not None:
            raise ValueError("Employee email already exists")

    for field, value in updates.items():
        setattr(
            employee,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise ValueError("Employee could not be updated")

    return employee


def terminate_employee(
    db: Session,
    employee_id: str,
) -> Employee:

    employee = get_employee(
        db,
        employee_id,
    )

    if employee.status == EmployeeStatus.TERMINATED:
        raise ValueError("Employee is already terminated")

    from datetime import date

    employee.status = EmployeeStatus.TERMINATED
    employee.termination_date = date.today()

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise ValueError("Employee could not be terminated")

    return employee
