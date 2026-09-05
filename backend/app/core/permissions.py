from fastapi import HTTPException, status

from app.models.user import User, UserRole

ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.ADMIN: {"*"},
    UserRole.HR: {
        "users:read", "employees:read", "employees:write",
        "departments:read", "departments:write", "contracts:read", "contracts:write",
        "schedules:read", "schedules:write", "attendance:read", "attendance:write",
        "timeoff:read", "timeoff:write", "salary:read", "salary:write",
        "payroll:read", "payroll:write", "dashboard:read",
    },
    UserRole.MANAGER: {
        "employees:read", "attendance:read", "attendance:write",
        "timeoff:read", "timeoff:write", "dashboard:read",
    },
    UserRole.EMPLOYEE: {
        "employees:self", "attendance:self", "timeoff:self", "payslips:self",
    },
}


def require_permission(user: User, permission: str) -> None:
    permissions = ROLE_PERMISSIONS.get(user.role, set())
    if "*" not in permissions and permission not in permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def require_roles(user: User, *roles: UserRole) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
