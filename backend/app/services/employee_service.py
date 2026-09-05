from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.employee import Employee, EmployeeStatus
from app.models.user import User


def list_employees(db: Session, page: int = 1, page_size: int = 20, search: str | None = None,
                   department_id: str | None = None, status: EmployeeStatus | None = None):
    stmt = select(Employee).options(selectinload(Employee.department)).order_by(Employee.last_name, Employee.first_name)
    filters = []
    if search:
        q = f"%{search}%"
        filters.append(or_(Employee.first_name.ilike(q), Employee.last_name.ilike(q), Employee.employee_number.ilike(q)))
    if department_id:
        filters.append(Employee.department_id == department_id)
    if status:
        filters.append(Employee.status == status)
    if filters:
        stmt = stmt.where(*filters)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    return items, total


def create_employee(db: Session, data: dict) -> Employee:
    if db.scalar(select(Employee).where(Employee.employee_number == data["employee_number"])):
        raise ValueError("Employee number already exists")
    if data.get("user_id") and db.get(User, data["user_id"]) is None:
        raise ValueError("User not found")
    employee = Employee(**data)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_employee(db: Session, employee_id: str) -> Employee:
    employee = db.get(Employee, employee_id)
    if not employee:
        raise ValueError("Employee not found")
    return employee


def update_employee(db: Session, employee: Employee, data: dict) -> Employee:
    if "employee_number" in data:
        other = db.scalar(select(Employee).where(Employee.employee_number == data["employee_number"], Employee.id != employee.id))
        if other:
            raise ValueError("Employee number already exists")
    if "user_id" in data and data["user_id"] and db.get(User, data["user_id"]) is None:
        raise ValueError("User not found")
    for key, value in data.items():
        setattr(employee, key, value)
    if employee.status == EmployeeStatus.TERMINATED and not employee.termination_date:
        raise ValueError("Terminated employees require termination_date")
    db.commit()
    db.refresh(employee)
    return employee
