from django.contrib import admin

from .models import TimeOffType, TimeOffAllocation, TimeOffRequest


@admin.register(TimeOffType)
class TimeOffTypeAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "unit",
        "requires_allocation",
        "is_paid",
        "is_active",
    )

    # represents main choices for a leave type
    list_filter = (
        "unit",
        "requires_allocation",
        "is_paid",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
    )


# admin config for employee leave allocations
@admin.register(TimeOffAllocation)
class TimeOffAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "time_off_type",
        "allocation_year",
        "allocated_days",
        "used_days",
        "remaining_days",
        "status",
        "valid_from",
        "valid_until",
    )

    list_filter = (
        "status",
        "allocation_year",
        "time_off_type",
    )

    search_fields = (
        "employee__employee_number",
        "employee__first_name",
        "employee__last_name",
    )

    autocomplete_fields = (
        "employee",
        "time_off_type",
        "reviewed_by",
    )


# admin config for employee leave requests
@admin.register(TimeOffRequest)
class TimeOffRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "time_off_type",
        "start_date",
        "end_date",
        "requested_days",
        "status",
    )

    list_filter = (
        "status",
        "time_off_type",
        "start_date",
    )

    search_fields = (
        "employee__employee_number",
        "employee__first_name",
        "employee__last_name",
    )

    autocomplete_fields = (
        "employee",
        "time_off_type",
        "reviewed_by",
    )

    date_hierarchy = "start_date"
