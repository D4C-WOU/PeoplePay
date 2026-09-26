from rest_framework.permissions import BasePermission

from users.models import User


class IsEmployee(BasePermission):
    # Allow only users with the Employee role
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.EMPLOYEE


class IsHRManager(BasePermission):
    # Allow HR Managers and higher roles
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.HR_MANAGER,
            User.Role.HR_PAYROLL_USER,
            User.Role.HR_PAYROLL_MANAGER,
            User.Role.ADMIN,
        ]


class IsHRPayrollUser(BasePermission):
    # Allow Payroll Users and higher roles
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.HR_PAYROLL_USER,
            User.Role.HR_PAYROLL_MANAGER,
            User.Role.ADMIN,
        ]


class IsHRPayrollManager(BasePermission):
    # Allow Payroll Managers and Admins
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.Role.HR_PAYROLL_MANAGER,
            User.Role.ADMIN,
        ]


class IsAdmin(BasePermission):
    # Allow only Admin users
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN
