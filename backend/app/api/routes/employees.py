from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.permissions import require_permission
from app.db.database import get_db
from app.models.employee import EmployeeStatus
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services import employee_service

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=list[EmployeeResponse])
def list_employees(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                   search: str | None = None, department_id: str | None = None,
                   status: EmployeeStatus | None = None, user=Depends(get_current_active_user),
                   db: Session = Depends(get_db)):
    require_permission(user, "employees:read")
    items, _ = employee_service.list_employees(db, page, page_size, search, department_id, status)
    return items


@router.post("", response_model=EmployeeResponse, status_code=201)
def create(data: EmployeeCreate, user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    require_permission(user, "employees:write")
    try: return employee_service.create_employee(db, data.model_dump())
    except ValueError as exc: raise HTTPException(409, str(exc))


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get(employee_id: str, user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    if user.role.value == "EMPLOYEE":
        if not user.employee or user.employee.id != employee_id: raise HTTPException(403, "Access denied")
    else: require_permission(user, "employees:read")
    try: return employee_service.get_employee(db, employee_id)
    except ValueError as exc: raise HTTPException(404, str(exc))


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update(employee_id: str, data: EmployeeUpdate, user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    if user.role.value == "EMPLOYEE":
        if not user.employee or user.employee.id != employee_id: raise HTTPException(403, "Access denied")
        # Self-service must not permit privilege/status/department changes.
        allowed = {"first_name","last_name","email","phone","address","emergency_contact_name","emergency_contact_phone"}
        payload = {k:v for k,v in data.model_dump(exclude_unset=True).items() if k in allowed}
    else:
        require_permission(user, "employees:write")
        payload = data.model_dump(exclude_unset=True)
    try: return employee_service.update_employee(db, employee_service.get_employee(db, employee_id), payload)
    except ValueError as exc: raise HTTPException(409, str(exc))


@router.delete("/{employee_id}", response_model=EmployeeResponse)
def deactivate(employee_id: str, user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    require_permission(user, "employees:write")
    try: return employee_service.update_employee(db, employee_service.get_employee(db, employee_id),
                                                  {"status": EmployeeStatus.TERMINATED})
    except ValueError as exc: raise HTTPException(409, str(exc))
