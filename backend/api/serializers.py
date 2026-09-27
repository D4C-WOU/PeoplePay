from rest_framework import serializers
from employees.models import Department
from users.models import User
from employees.models import Department, Employee, WorkSchedule, WorkScheduleDay
from contracts.models import Contract
from attendance.models import AttendanceRecord
from time_off.models import (
    TimeOffType,
    TimeOffAllocation,
    TimeOffRequest,
)
from payroll.models import (
    SalaryStructure,
    SalaryRule,
)


class CurrentUserSerializer(serializers.ModelSerializer):
    # Return the user's basic account information
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = fields


class DepartmentSerializer(serializers.ModelSerializer):
    # Serialize department information for the API
    class Meta:
        model = Department
        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_active",
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    # Show related names instead of only database IDs
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    manager_name = serializers.CharField(
        source="manager.full_name",
        read_only=True,
    )
    work_schedule_name = serializers.CharField(
        source="work_schedule.name",
        read_only=True,
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_number",
            "user",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "date_of_birth",
            "hire_date",
            "termination_date",
            "job_title",
            "department",
            "department_name",
            "manager",
            "manager_name",
            "work_schedule",
            "work_schedule_name",
            "employee_type",
            "status",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "bank_name",
            "bank_account_number",
            "bank_ifsc",
        ]

        # These values are calculated or controlled by the backend
        read_only_fields = [
            "id",
            "full_name",
            "department_name",
            "manager_name",
            "work_schedule_name",
        ]


class WorkScheduleDaySerializer(serializers.ModelSerializer):
    # Return the schedule day information
    day_name = serializers.CharField(
        source="get_day_of_week_display",
        read_only=True,
    )

    class Meta:
        model = WorkScheduleDay
        fields = [
            "id",
            "day_of_week",
            "day_name",
            "start_time",
            "end_time",
            "break_minutes",
        ]
        read_only_fields = [
            "id",
            "day_name",
        ]


class WorkScheduleSerializer(serializers.ModelSerializer):
    # Include the weekly pattern inside the schedule response
    days = WorkScheduleDaySerializer(
        many=True,
        read_only=True,
    )

    # Return the calculated weekly hours
    weekly_hours = serializers.FloatField(
        read_only=True,
    )

    class Meta:
        model = WorkSchedule
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "weekly_hours",
            "days",
        ]
        read_only_fields = [
            "id",
            "weekly_hours",
            "days",
        ]


class ContractSerializer(serializers.ModelSerializer):
    # Show related names in the API response
    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )
    salary_structure_name = serializers.CharField(
        source="salary_structure.name",
        read_only=True,
    )
    work_schedule_name = serializers.CharField(
        source="work_schedule.name",
        read_only=True,
    )

    class Meta:
        model = Contract
        fields = [
            "id",
            "contract_number",
            "employee",
            "employee_name",
            "salary_structure",
            "salary_structure_name",
            "work_schedule",
            "work_schedule_name",
            "start_date",
            "end_date",
            "contract_type",
            "base_salary",
            "currency",
            "status",
            "notes",
        ]
        read_only_fields = [
            "id",
            "employee_name",
            "salary_structure_name",
            "work_schedule_name",
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    # Show related employee and schedule names
    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )
    work_schedule_name = serializers.CharField(
        source="work_schedule.name",
        read_only=True,
    )
    corrected_by_name = serializers.CharField(
        source="corrected_by.username",
        read_only=True,
    )

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "employee",
            "employee_name",
            "work_schedule",
            "work_schedule_name",
            "attendance_date",
            "check_in",
            "check_out",
            "expected_hours",
            "worked_hours",
            "overtime_hours",
            "status",
            "notes",
            "corrected_by",
            "corrected_by_name",
            "corrected_at",
        ]
        read_only_fields = [
            "id",
            "employee_name",
            "work_schedule_name",
            "corrected_by",
            "corrected_by_name",
            "corrected_at",
        ]


class TimeOffTypeSerializer(serializers.ModelSerializer):
    # Show the basic information needed by the frontend
    class Meta:
        model = TimeOffType
        fields = [
            "id",
            "name",
            "code",
            "description",
            "unit",
            "requires_allocation",
            "requires_approval",
            "affects_payroll",
            "is_active",
        ]
        read_only_fields = ["id"]


class TimeOffAllocationSerializer(serializers.ModelSerializer):
    # Show employee and leave type names alongside their IDs
    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )
    time_off_type_name = serializers.CharField(
        source="time_off_type.name",
        read_only=True,
    )

    # Calculate remaining balance for display
    remaining_days = serializers.SerializerMethodField()

    class Meta:
        model = TimeOffAllocation
        fields = [
            "id",
            "employee",
            "employee_name",
            "time_off_type",
            "time_off_type_name",
            "allocated_days",
            "taken_days",
            "remaining_days",
            "valid_from",
            "valid_to",
            "status",
        ]
        read_only_fields = [
            "id",
            "employee_name",
            "time_off_type_name",
            "taken_days",
            "remaining_days",
        ]

    def get_remaining_days(self, obj):
        # Remaining balance is allocation minus approved/taken days
        return obj.allocated_days - obj.taken_days


class TimeOffRequestSerializer(serializers.ModelSerializer):
    # Show related employee and leave type names
    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )
    time_off_type_name = serializers.CharField(
        source="time_off_type.name",
        read_only=True,
    )

    class Meta:
        model = TimeOffRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "time_off_type",
            "time_off_type_name",
            "start_date",
            "end_date",
            "duration_days",
            "reason",
            "status",
            "created_at",
            "approved_by",
            "approved_at",
        ]
        read_only_fields = [
            "id",
            "employee_name",
            "time_off_type_name",
            "duration_days",
            "status",
            "created_at",
            "approved_by",
            "approved_at",
        ]


class MyEmployeeSerializer(serializers.ModelSerializer):
    # Show the employee's department name
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    # Show the employee's work schedule name
    work_schedule_name = serializers.CharField(
        source="work_schedule.name",
        read_only=True,
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_number",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "date_of_birth",
            "hire_date",
            "job_title",
            "department",
            "department_name",
            "manager",
            "work_schedule",
            "work_schedule_name",
            "employee_type",
            "status",
        ]
        read_only_fields = fields


class MyAttendanceSerializer(serializers.ModelSerializer):
    # Show the schedule name instead of only its ID
    work_schedule_name = serializers.CharField(
        source="work_schedule.name",
        read_only=True,
    )

    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "attendance_date",
            "check_in",
            "check_out",
            "expected_hours",
            "worked_hours",
            "overtime_hours",
            "status",
            "work_schedule",
            "work_schedule_name",
            "notes",
        ]
        read_only_fields = fields


class MyTimeOffRequestSerializer(serializers.ModelSerializer):
    # Show the leave type name in the employee response
    time_off_type_name = serializers.CharField(
        source="time_off_type.name",
        read_only=True,
    )

    class Meta:
        model = TimeOffRequest
        fields = [
            "id",
            "time_off_type",
            "time_off_type_name",
            "start_date",
            "end_date",
            "requested_days",
            "reason",
            "status",
            "reviewed_at",
        ]
        read_only_fields = fields


class SalaryStructureSerializer(serializers.ModelSerializer):
    # Show the number of rules configured for this structure
    rule_count = serializers.IntegerField(
        source="rules.count",
        read_only=True,
    )

    class Meta:
        model = SalaryStructure
        fields = [
            "id",
            "code",
            "name",
            "description",
            "currency",
            "is_active",
            "rule_count",
        ]
        read_only_fields = [
            "id",
            "rule_count",
        ]


class SalaryRuleSerializer(serializers.ModelSerializer):
    # Show the parent salary structure name
    salary_structure_name = serializers.CharField(
        source="salary_structure.name",
        read_only=True,
    )

    class Meta:
        model = SalaryRule
        fields = [
            "id",
            "salary_structure",
            "salary_structure_name",
            "code",
            "name",
            "category",
            "sequence",
            "calculation_type",
            "amount",
            "percentage",
            "formula",
        ]
        read_only_fields = [
            "id",
            "salary_structure_name",
        ]
