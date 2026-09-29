from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

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
    Payrun,
    Payslip,
    PayslipLine,
)

from .dashboard import get_dashboard_data
from payroll.services import calculate_salary_rules
from contracts.services import get_applicable_contract

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
    PayrunSerializer,
    PayslipSerializer,
    DashboardSerializer,
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


class PayrunViewSet(ModelViewSet):
    # Load payruns together with their payroll configuration
    queryset = (
        Payrun.objects.select_related(
            "salary_structure",
        )
        .prefetch_related(
            "selected_employees",
            "payslips__lines",
        )
        .order_by(
            "-period_start",
            "-created_at",
        )
    )

    # Convert payruns into API responses
    serializer_class = PayrunSerializer

    def get_permissions(self):
        # Import payroll permissions
        from .permissions import (
            IsHRPayrollUser,
            IsHRPayrollManager,
        )

        # Payroll users can view payruns
        if self.action in [
            "list",
            "retrieve",
        ]:
            permission_classes = [
                IsHRPayrollUser,
            ]

        # Payroll managers can create and process payruns
        elif self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "compute",
            "validation",
            "validate_payrun",
            "mark_paid",
        ]:
            permission_classes = [
                IsHRPayrollManager,
            ]

        # Protect unexpected actions
        else:
            permission_classes = [
                IsAuthenticated,
            ]

        # Create the permission objects
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Start with the normal payrun queryset
        queryset = super().get_queryset()

        # Allow filtering by payroll status
        status_filter = self.request.query_params.get(
            "status",
        )

        if status_filter:
            queryset = queryset.filter(
                status=status_filter,
            )

        # Allow filtering by salary structure
        salary_structure_id = self.request.query_params.get(
            "salary_structure",
        )

        if salary_structure_id:
            queryset = queryset.filter(
                salary_structure_id=salary_structure_id,
            )

        return queryset

    def create(self, request, *args, **kwargs):
        # Copy the incoming data so we can process employee IDs
        data = request.data.copy()

        # Read the selected employees from the request
        employee_ids = data.pop(
            "selected_employees",
            [],
        )

        # DRF may receive this as a single value
        if isinstance(employee_ids, str):
            employee_ids = [employee_ids]

        # A payrun must contain at least one employee
        if not employee_ids:
            return Response(
                {"detail": "At least one employee must be selected."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the basic payrun fields
        serializer = self.get_serializer(
            data=data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        # Save the payrun
        payrun = serializer.save()

        # Add the selected employees to the payrun
        payrun.selected_employees.set(
            employee_ids,
        )

        # Store the employee count
        payrun.employee_count = payrun.selected_employees.count()

        payrun.save(
            update_fields=[
                "employee_count",
            ]
        )

        # Return the completed payrun
        output_serializer = self.get_serializer(
            payrun,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="compute",
    )
    @transaction.atomic
    def compute(self, request, pk=None):
        # Load the payrun inside the transaction
        payrun = self.get_object()

        # Only draft payruns can be computed
        if payrun.status != Payrun.Status.DRAFT:
            return Response(
                {"detail": ("Only DRAFT payruns can be computed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # A payrun needs at least one employee
        employees = list(
            payrun.selected_employees.select_related(
                "department",
            )
        )

        if not employees:
            return Response(
                {"detail": ("At least one employee must be selected.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Remove old draft payslips before recalculating
        payrun.payslips.filter(
            status=Payslip.Status.DRAFT,
        ).delete()

        # Keep track of payrun totals
        gross_total = Decimal("0.00")
        deduction_total = Decimal("0.00")
        net_total = Decimal("0.00")

        # Process each selected employee
        for employee in employees:
            # Find the contract covering the complete payroll period
            contract = get_applicable_contract(
                employee,
                payrun.period_start,
                payrun.period_end,
            )

            # Make sure the contract uses the payrun structure
            if contract.salary_structure_id != payrun.salary_structure_id:
                raise ValidationError(
                    (
                        f"{employee.full_name} has a contract using "
                        "a different salary structure."
                    )
                )

            # Calculate salary rules using the contract salary
            results = calculate_salary_rules(
                payrun.salary_structure,
                contract.base_salary,
            )

            # Start payslip totals
            gross_amount = Decimal("0.00")
            deduction_amount = Decimal("0.00")

            # Create the payslip first
            payslip = Payslip.objects.create(
                payrun=payrun,
                employee=employee,
                contract=contract,
                salary_structure=payrun.salary_structure,
                period_start=payrun.period_start,
                period_end=payrun.period_end,
                employee_number_snapshot=employee.employee_number,
                employee_name_snapshot=employee.full_name,
                currency=contract.currency,
                status=Payslip.Status.DRAFT,
                generated_at=timezone.now(),
            )

            # Create one payslip line for every calculated rule
            for rule_code, result in results.items():
                rule = result["rule"]
                amount = result["amount"]

                # Earnings contribute to gross salary
                if rule.category in [
                    SalaryRule.Category.BASIC,
                    SalaryRule.Category.ALLOWANCE,
                ]:
                    gross_amount += amount

                # Deductions reduce the final salary
                elif rule.category == SalaryRule.Category.DEDUCTION:
                    deduction_amount += amount

                # Store the calculated rule result
                PayslipLine.objects.create(
                    payslip=payslip,
                    salary_rule=rule,
                    code=rule.code,
                    name=rule.name,
                    category=rule.category,
                    sequence=rule.sequence,
                    base_amount=contract.base_salary,
                    calculated_amount=amount,
                    description=(
                        f"{rule.name} calculated from " f"salary rule {rule.code}."
                    ),
                )

            # Calculate final net salary
            net_amount = gross_amount - deduction_amount

            # Prevent negative net salary
            if net_amount < 0:
                net_amount = Decimal("0.00")

            # Save calculated totals
            payslip.gross_amount = gross_amount
            payslip.deduction_amount = deduction_amount
            payslip.net_amount = net_amount

            payslip.save(
                update_fields=[
                    "gross_amount",
                    "deduction_amount",
                    "net_amount",
                ]
            )

            # Add this employee to the payrun totals
            gross_total += gross_amount
            deduction_total += deduction_amount
            net_total += net_amount

        # Save aggregated payrun totals
        payrun.employee_count = len(employees)
        payrun.gross_total = gross_total
        payrun.deduction_total = deduction_total
        payrun.net_total = net_total
        payrun.status = Payrun.Status.COMPUTED

        payrun.save(
            update_fields=[
                "employee_count",
                "gross_total",
                "deduction_total",
                "net_total",
                "status",
            ]
        )

        # Return the newly computed payrun
        serializer = self.get_serializer(
            payrun,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="validation",
    )
    def validation(self, request, pk=None):
        # Load the payrun
        payrun = self.get_object()

        # Store all payroll warnings
        warnings = []

        # A payrun should contain employees
        employees = list(payrun.selected_employees.all())

        if not employees:
            warnings.append("No employees are selected for this payrun.")

        # Check every selected employee
        for employee in employees:
            # Missing bank details are important before payment
            if not employee.bank_account_number:
                warnings.append(
                    f"{employee.full_name} is missing bank account details."
                )

            # Check for an applicable contract
            try:
                contract = get_applicable_contract(
                    employee,
                    payrun.period_start,
                    payrun.period_end,
                )
            except ValidationError as exc:
                warnings.append(f"{employee.full_name}: {exc}")
                continue

            # Contract structure must match the payrun structure
            if contract.salary_structure_id != payrun.salary_structure_id:
                warnings.append(
                    (
                        f"{employee.full_name} has a contract using "
                        "a different salary structure."
                    )
                )

            # Check for duplicate payslips outside this payrun
            duplicate_exists = (
                Payslip.objects.filter(
                    employee=employee,
                    period_start=payrun.period_start,
                    period_end=payrun.period_end,
                )
                .exclude(
                    payrun=payrun,
                )
                .exists()
            )

            if duplicate_exists:
                warnings.append(
                    (f"{employee.full_name} already has a " "payslip for this period.")
                )

        # Computed payruns should have payslips
        if payrun.status in [
            Payrun.Status.COMPUTED,
            Payrun.Status.VALIDATED,
            Payrun.Status.PAID,
        ]:
            if not payrun.payslips.exists():
                warnings.append("This payrun has no generated payslips.")

        # Return validation information
        return Response(
            {
                "payrun_id": payrun.id,
                "status": payrun.status,
                "valid": len(warnings) == 0,
                "warnings": warnings,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="validate",
    )
    @transaction.atomic
    def validate_payrun(self, request, pk=None):
        # Load the payrun
        payrun = self.get_object()

        # Only computed payruns can be validated
        if payrun.status != Payrun.Status.COMPUTED:
            return Response(
                {"detail": ("Only COMPUTED payruns can be validated.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check the same warnings used by the validation endpoint
        employees = list(payrun.selected_employees.all())

        warnings = []

        for employee in employees:
            if not employee.bank_account_number:
                warnings.append(
                    f"{employee.full_name} is missing bank account details."
                )

            try:
                contract = get_applicable_contract(
                    employee,
                    payrun.period_start,
                    payrun.period_end,
                )
            except ValidationError as exc:
                warnings.append(f"{employee.full_name}: {exc}")
                continue

            if contract.salary_structure_id != payrun.salary_structure_id:
                warnings.append(
                    (
                        f"{employee.full_name} has a contract using "
                        "a different salary structure."
                    )
                )

            duplicate_exists = (
                Payslip.objects.filter(
                    employee=employee,
                    period_start=payrun.period_start,
                    period_end=payrun.period_end,
                )
                .exclude(
                    payrun=payrun,
                )
                .exists()
            )

            if duplicate_exists:
                warnings.append(
                    (f"{employee.full_name} already has a " "payslip for this period.")
                )

        # Do not finalize payroll while warnings exist
        if warnings:
            return Response(
                {
                    "detail": (
                        "Payrun cannot be validated because " "payroll warnings exist."
                    ),
                    "warnings": warnings,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Finalize every generated payslip
        payrun.payslips.update(
            status=Payslip.Status.FINALIZED,
        )

        # Mark the payrun as validated
        payrun.status = Payrun.Status.VALIDATED

        payrun.save(
            update_fields=[
                "status",
            ]
        )

        # Return the updated payrun
        serializer = self.get_serializer(
            payrun,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="paid",
    )
    @transaction.atomic
    def mark_paid(self, request, pk=None):
        # Load the payrun
        payrun = self.get_object()

        # Only validated payruns can be marked paid
        if payrun.status != Payrun.Status.VALIDATED:
            return Response(
                {"detail": ("Only VALIDATED payruns can be marked as paid.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Require a payment date before marking payroll as paid
        if not payrun.payment_date:
            return Response(
                {
                    "detail": (
                        "A payment date is required before "
                        "marking the payrun as paid."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark every payslip as paid
        payrun.payslips.update(
            status=Payslip.Status.PAID,
        )

        # Mark the parent payrun as paid
        payrun.status = Payrun.Status.PAID

        payrun.save(
            update_fields=[
                "status",
            ]
        )

        # Return the updated payroll batch
        serializer = self.get_serializer(
            payrun,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class PayslipViewSet(ModelViewSet):
    # Load payslips with their related payroll information
    queryset = (
        Payslip.objects.select_related(
            "payrun",
            "employee",
            "contract",
            "salary_structure",
        )
        .prefetch_related(
            "lines",
        )
        .order_by(
            "-period_start",
            "employee_name_snapshot",
        )
    )

    # Convert payslips into API responses
    serializer_class = PayslipSerializer

    def get_permissions(self):
        # Import payroll permissions
        from .permissions import (
            IsHRPayrollUser,
            IsHRPayrollManager,
        )

        # Payroll users can read payslips
        if self.action in [
            "list",
            "retrieve",
        ]:
            permission_classes = [
                IsHRPayrollUser,
            ]

        # Payroll managers can modify payslips
        elif self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            permission_classes = [
                IsHRPayrollManager,
            ]

        # Protect unexpected actions
        else:
            permission_classes = [
                IsAuthenticated,
            ]

        # Create the permission objects
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Start with all payslips
        queryset = super().get_queryset()

        # Filter by employee
        employee_id = self.request.query_params.get(
            "employee",
        )

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id,
            )

        # Filter by payrun
        payrun_id = self.request.query_params.get(
            "payrun",
        )

        if payrun_id:
            queryset = queryset.filter(
                payrun_id=payrun_id,
            )

        # Filter by status
        status_filter = self.request.query_params.get(
            "status",
        )

        if status_filter:
            queryset = queryset.filter(
                status=status_filter,
            )

        return queryset

        contract = get_applicable_contract(
            employee,
            payrun.period_start,
            payrun.period_end,
        )


class DashboardView(APIView):
    # Dashboard is available to authenticated users
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Build the current dashboard data
        data = get_dashboard_data()

        # Return the dashboard as JSON
        serializer = DashboardSerializer(data)

        return Response(serializer.data)
