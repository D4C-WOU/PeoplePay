from django.core.exceptions import ValidationError
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from attendance.models import AttendanceRecord
from attendance.services import update_attendance_hours
from contracts.models import Contract
from employees.models import (
    Department,
    Employee,
    WorkSchedule,
    WorkScheduleDay,
)
from time_off.models import (
    TimeOffAllocation,
    TimeOffRequest,
    TimeOffType,
)
from payroll.models import (
    SalaryStructure,
    SalaryRule,
)


from time_off.services import (
    approve_time_off_request,
    reject_time_off_request,
)

from .permissions import (
    IsAdmin,
    IsHRManager,
    IsHRPayrollManager,
    IsHRPayrollUser,
)
from .serializers import (
    AttendanceSerializer,
    ContractSerializer,
    CurrentUserSerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    TimeOffAllocationSerializer,
    TimeOffRequestSerializer,
    TimeOffTypeSerializer,
    WorkScheduleDaySerializer,
    WorkScheduleSerializer,
    MyEmployeeSerializer,
    MyTimeOffRequestSerializer,
    MyAttendanceSerializer,
    SalaryRuleSerializer,
    SalaryStructureSerializer,
)


class CurrentUserView(APIView):
    # Require a valid JWT before returning user information
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Serialize the authenticated user
        serializer = CurrentUserSerializer(request.user)

        # Return the current user's account information
        return Response(serializer.data)


class HRManagerTestView(APIView):
    # Require HR Manager access or higher
    permission_classes = [IsHRManager]

    def get(self, request):
        # Confirm that the current user passed the permission check
        return Response(
            {
                "message": "HR Manager access granted.",
                "role": request.user.role,
            }
        )


class HRPayrollUserTestView(APIView):
    # Require Payroll User access or higher
    permission_classes = [IsHRPayrollUser]

    def get(self, request):
        # Confirm that the current user passed the permission check
        return Response(
            {
                "message": "HR Payroll User access granted.",
                "role": request.user.role,
            }
        )


class HRPayrollManagerTestView(APIView):
    # Require HR Payroll Manager access or higher
    permission_classes = [IsHRPayrollManager]

    def get(self, request):
        # Confirm that the current user passed the permission check
        return Response(
            {
                "message": "HR Payroll Manager access granted.",
                "role": request.user.role,
            }
        )


class AdminTestView(APIView):
    # Require Admin access
    permission_classes = [IsAdmin]

    def get(self, request):
        # Confirm that the current user passed the permission check
        return Response(
            {
                "message": "Admin access granted.",
                "role": request.user.role,
            }
        )


class DepartmentViewSet(ModelViewSet):
    # Return departments ordered alphabetically
    queryset = Department.objects.all().order_by("name")

    # Convert departments into API responses
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        # Import permissions here to keep role rules close to the API
        from .permissions import IsHRManager, IsHRPayrollManager

        # Allow HR roles to view and create/update departments
        if self.action in [
            "list",
            "retrieve",
            "create",
            "update",
            "partial_update",
        ]:
            permission_classes = [IsHRManager]

        # Restrict department deletion to Payroll Managers and Admins
        elif self.action == "destroy":
            permission_classes = [IsHRPayrollManager]

        # Use authentication for any unexpected action
        else:
            permission_classes = [IsAuthenticated]

        # Create the permission objects required by DRF
        return [permission() for permission in permission_classes]


class EmployeeViewSet(ModelViewSet):
    # Return employees in employee-number order
    queryset = Employee.objects.select_related(
        "user",
        "department",
        "manager",
        "work_schedule",
    ).order_by("employee_number")

    # Convert employees into API responses
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        # Import the HR permission used by this API
        from .permissions import IsHRManager

        # HR roles and Admin can manage employee records
        permission_classes = [IsHRManager]

        # Create the permission objects required by DRF
        return [permission() for permission in permission_classes]


class WorkScheduleViewSet(ModelViewSet):
    # Return schedules with their weekly days
    queryset = WorkSchedule.objects.prefetch_related(
        "days",
    ).order_by("name")

    # Convert schedules into API responses
    serializer_class = WorkScheduleSerializer

    # HR roles can manage working schedules
    permission_classes = [IsHRManager]


class WorkScheduleDayViewSet(ModelViewSet):
    # Return schedule days in weekday order
    queryset = WorkScheduleDay.objects.select_related(
        "work_schedule",
    ).order_by(
        "work_schedule",
        "day_of_week",
    )

    # Convert schedule days into API responses
    serializer_class = WorkScheduleDaySerializer

    # HR roles can manage schedule days
    permission_classes = [IsHRManager]

    def get_queryset(self):
        # Start with all schedule days
        queryset = super().get_queryset()

        # Allow filtering by parent schedule
        schedule_id = self.request.query_params.get("work_schedule")

        if schedule_id:
            queryset = queryset.filter(
                work_schedule_id=schedule_id,
            )

        return queryset


class ContractViewSet(ModelViewSet):
    # Return contracts with their related employee and payroll data
    queryset = Contract.objects.select_related(
        "employee",
        "salary_structure",
        "work_schedule",
    ).order_by(
        "-start_date",
    )

    # Convert contracts into API responses
    serializer_class = ContractSerializer

    # HR roles can manage employee contracts
    permission_classes = [IsHRManager]

    def get_queryset(self):
        # Start with all contracts
        queryset = super().get_queryset()

        # Allow filtering contracts by employee
        employee_id = self.request.query_params.get("employee")

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id,
            )

        # Allow filtering contracts by status
        status_filter = self.request.query_params.get("status")

        if status_filter:
            queryset = queryset.filter(
                status=status_filter,
            )

        return queryset


class AttendanceViewSet(ModelViewSet):
    # Return attendance with related employee and schedule data
    queryset = AttendanceRecord.objects.select_related(
        "employee",
        "work_schedule",
        "corrected_by",
    ).order_by(
        "-attendance_date",
    )

    # Convert attendance records into API responses
    serializer_class = AttendanceSerializer

    # HR roles can manage attendance
    permission_classes = [IsHRManager]

    def get_queryset(self):
        # Start with all attendance records
        queryset = super().get_queryset()

        # Allow filtering by employee
        employee_id = self.request.query_params.get("employee")

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id,
            )

        # Allow filtering by attendance date
        attendance_date = self.request.query_params.get(
            "attendance_date",
        )

        if attendance_date:
            queryset = queryset.filter(
                attendance_date=attendance_date,
            )

        # Allow filtering by status
        status_filter = self.request.query_params.get("status")

        if status_filter:
            queryset = queryset.filter(
                status=status_filter,
            )

        return queryset

    def perform_update(self, serializer):
        # Save the attendance correction and audit information
        attendance = serializer.save(
            corrected_by=self.request.user,
            corrected_at=timezone.now(),
        )

        # Recalculate worked and overtime hours
        update_attendance_hours(attendance)


class TimeOffTypeViewSet(ModelViewSet):
    # Return leave types ordered alphabetically
    queryset = TimeOffType.objects.all().order_by("name")

    # Convert leave types into API responses
    serializer_class = TimeOffTypeSerializer

    # HR roles can manage leave types
    permission_classes = [IsHRManager]

    def get_queryset(self):
        # Start with all leave types
        queryset = super().get_queryset()

        # Allow filtering active and inactive leave types
        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            queryset = queryset.filter(
                is_active=is_active.lower() == "true",
            )

        return queryset


class TimeOffAllocationViewSet(ModelViewSet):
    # Return allocations with related employee and leave type data
    queryset = TimeOffAllocation.objects.select_related(
        "employee",
        "time_off_type",
        "reviewed_by",
    ).order_by(
        "-allocation_year",
    )

    # Convert allocations into API responses
    serializer_class = TimeOffAllocationSerializer

    # HR roles can manage leave allocations
    permission_classes = [IsHRManager]

    def get_queryset(self):
        # Start with all allocations
        queryset = super().get_queryset()

        # Allow filtering by employee
        employee_id = self.request.query_params.get("employee")

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id,
            )

        # Allow filtering by leave type
        time_off_type_id = self.request.query_params.get(
            "time_off_type",
        )

        if time_off_type_id:
            queryset = queryset.filter(
                time_off_type_id=time_off_type_id,
            )

        # Allow filtering by allocation status
        allocation_status = self.request.query_params.get("status")

        if allocation_status:
            queryset = queryset.filter(
                status=allocation_status,
            )

        return queryset


class TimeOffRequestViewSet(ModelViewSet):
    # Return requests with related employee and leave type data
    queryset = TimeOffRequest.objects.select_related(
        "employee",
        "time_off_type",
        "reviewed_by",
    ).order_by(
        "-start_date",
    )

    # Convert requests into API responses
    serializer_class = TimeOffRequestSerializer

    # HR roles can manage time-off requests
    permission_classes = [IsHRManager]

    def get_queryset(self):
        # Start with all time-off requests
        queryset = super().get_queryset()

        # Allow filtering by employee
        employee_id = self.request.query_params.get("employee")

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id,
            )

        # Allow filtering by leave type
        time_off_type_id = self.request.query_params.get(
            "time_off_type",
        )

        if time_off_type_id:
            queryset = queryset.filter(
                time_off_type_id=time_off_type_id,
            )

        # Allow filtering by request status
        request_status = self.request.query_params.get("status")

        if request_status:
            queryset = queryset.filter(
                status=request_status,
            )

        return queryset

    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
    )
    def approve(self, request, pk=None):
        # Get the selected time-off request
        time_off_request = self.get_object()

        try:
            # Run the existing business logic
            approved_request, allocation = approve_time_off_request(
                time_off_request,
                request.user,
            )
        except ValidationError as exc:
            # Return business-rule errors as a client error
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return the updated request
        serializer = self.get_serializer(
            approved_request,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reject",
    )
    def reject(self, request, pk=None):
        # Get the selected time-off request
        time_off_request = self.get_object()

        try:
            # Run the existing rejection business logic
            rejected_request = reject_time_off_request(
                time_off_request,
                request.user,
            )
        except ValidationError as exc:
            # Return business-rule errors as a client error
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Return the updated request
        serializer = self.get_serializer(
            rejected_request,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class MyEmployeeView(APIView):
    # Require a logged-in user
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Find the employee record linked to the logged-in user
        employee = Employee.objects.select_related(
            "department",
            "manager",
            "work_schedule",
        ).get(user=request.user)

        # Serialize only the current employee's information
        serializer = MyEmployeeSerializer(employee)

        # Return the employee's own data
        return Response(serializer.data)


class MyAttendanceView(APIView):
    # Require a logged-in user
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Find the current employee
        employee = Employee.objects.get(user=request.user)

        # Get only this employee's attendance records
        attendance = (
            AttendanceRecord.objects.filter(
                employee=employee,
            )
            .select_related(
                "work_schedule",
            )
            .order_by("-attendance_date")
        )

        # Serialize the employee's attendance history
        serializer = MyAttendanceSerializer(
            attendance,
            many=True,
        )

        # Return the attendance history
        return Response(serializer.data)


class MyTimeOffView(APIView):
    # Require a logged-in user
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Find the current employee
        employee = Employee.objects.get(user=request.user)

        # Get only this employee's leave requests
        requests = (
            TimeOffRequest.objects.filter(
                employee=employee,
            )
            .select_related(
                "time_off_type",
            )
            .order_by("-start_date")
        )

        # Serialize the employee's leave history
        serializer = MyTimeOffRequestSerializer(
            requests,
            many=True,
        )

        # Return the leave requests
        return Response(serializer.data)


class SalaryStructureViewSet(ModelViewSet):
    # Return salary structures with their rules available
    queryset = SalaryStructure.objects.prefetch_related(
        "rules",
    ).order_by("name")

    # Convert salary structures into API responses
    serializer_class = SalaryStructureSerializer

    def get_permissions(self):
        # Import the permissions used by payroll roles
        from .permissions import IsHRPayrollUser, IsHRPayrollManager

        # Payroll users can read salary structures
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsHRPayrollUser]

        # Payroll managers and Admins can modify salary structures
        elif self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            permission_classes = [IsHRPayrollManager]

        # Protect unexpected actions with authentication
        else:
            permission_classes = [IsAuthenticated]

        # Create the permission objects required by DRF
        return [permission() for permission in permission_classes]


class SalaryRuleViewSet(ModelViewSet):
    # Return rules with their parent salary structure
    queryset = SalaryRule.objects.select_related(
        "salary_structure",
    ).order_by(
        "salary_structure",
        "sequence",
    )

    # Convert salary rules into API responses
    serializer_class = SalaryRuleSerializer

    def get_permissions(self):
        # Import the permissions used by payroll roles
        from .permissions import IsHRPayrollUser, IsHRPayrollManager

        # Payroll users can read salary rules
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsHRPayrollUser]

        # Payroll managers and Admins can modify salary rules
        elif self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            permission_classes = [IsHRPayrollManager]

        # Protect unexpected actions with authentication
        else:
            permission_classes = [IsAuthenticated]

        # Create the permission objects required by DRF
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Start with all salary rules
        queryset = super().get_queryset()

        # Allow filtering rules by salary structure
        structure_id = self.request.query_params.get("salary_structure")

        if structure_id:
            queryset = queryset.filter(salary_structure_id=structure_id)

        return queryset
