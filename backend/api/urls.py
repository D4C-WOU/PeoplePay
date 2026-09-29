from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

from .views import (
    AdminTestView,
    CurrentUserView,
    DepartmentViewSet,
    HRManagerTestView,
    HRPayrollManagerTestView,
    HRPayrollUserTestView,
    EmployeeViewSet,
    WorkScheduleDayViewSet,
    WorkScheduleViewSet,
    ContractViewSet,
    AttendanceViewSet,
    TimeOffTypeViewSet,
    TimeOffAllocationViewSet,
    TimeOffRequestViewSet,
    MyEmployeeView,
    MyAttendanceView,
    MyTimeOffView,
    SalaryStructureViewSet,
    SalaryRuleViewSet,
    PayrunViewSet,
    PayslipViewSet,
    DashboardView,
)

router = DefaultRouter()


# Register the department CRUD API
router.register(
    "departments",
    DepartmentViewSet,
    basename="department",
)


# Register the employee CRUD API
router.register(
    "employees",
    EmployeeViewSet,
    basename="employee",
)


# Register the work schedule CRUD API
router.register(
    "work-schedules",
    WorkScheduleViewSet,
    basename="work-schedule",
)


# Register the individual schedule day CRUD API
router.register(
    "work-schedule-days",
    WorkScheduleDayViewSet,
    basename="work-schedule-day",
)


# Register the contracts CRUD API
router.register(
    "contracts",
    ContractViewSet,
    basename="contract",
)


# Register the attendance record CRUD API
router.register(
    "attendance",
    AttendanceViewSet,
    basename="attendance",
)


# Register the time-off type CRUD API
router.register(
    "time-off/types",
    TimeOffTypeViewSet,
    basename="time-off-type",
)


# Register the time-off allocation CRUD API
router.register(
    "time-off/allocations",
    TimeOffAllocationViewSet,
    basename="time-off-allocation",
)


# Register the time-off request CRUD API
router.register(
    "time-off/requests",
    TimeOffRequestViewSet,
    basename="time-off-request",
)

# Register the salary structure CRUD API
router.register(
    "salary-structures",
    SalaryStructureViewSet,
    basename="salary-structure",
)


# Register the salary rule CRUD API
router.register(
    "salary-rules",
    SalaryRuleViewSet,
    basename="salary-rule",
)

# Register the payruns API
router.register(
    "payruns",
    PayrunViewSet,
    basename="payrun",
)

# Register the payslips API
router.register(
    "payslips",
    PayslipViewSet,
    basename="payslip",
)

urlpatterns = [
    # Login and receive access + refresh tokens
    path(
        "auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    # Get a new access token using a refresh token
    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    # Get information about the currently authenticated user
    path(
        "auth/me/",
        CurrentUserView.as_view(),
        name="current_user",
    ),
    # Return the authenticated employee's own HR information
    path(
        "me/employee/",
        MyEmployeeView.as_view(),
        name="my_employee",
    ),
    # Return the authenticated employee's attendance history
    path(
        "me/attendance/",
        MyAttendanceView.as_view(),
        name="my_attendance",
    ),
    # Return the authenticated employee's time-off history
    path(
        "me/time-off/",
        MyTimeOffView.as_view(),
        name="my_time_off",
    ),
    # RBAC test endpoints
    path(
        "rbac/hr-manager/",
        HRManagerTestView.as_view(),
        name="rbac_hr_manager",
    ),
    path(
        "rbac/payroll-user/",
        HRPayrollUserTestView.as_view(),
        name="rbac_payroll_user",
    ),
    path(
        "rbac/payroll-manager/",
        HRPayrollManagerTestView.as_view(),
        name="rbac_payroll_manager",
    ),
    path(
        "rbac/admin/",
        AdminTestView.as_view(),
        name="rbac_admin",
    ),
    path(
        "dashboard/",
        DashboardView.as_view(),
        name="dashboard",
    ),
]


# Add all registered router endpoints to the URL configuration
urlpatterns += router.urls
