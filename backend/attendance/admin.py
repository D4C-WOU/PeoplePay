from django.contrib import admin

from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):

    # main attendance info shown in the list
    list_display = (
        "employee",
        "attendance_date",
        "status",
        "check_in",
        "check_out",
        "worked_hours",
        "overtime_hours",
    )

    list_filter = (
        "status",
        "attendance_date",
        "work_schedule",
    )

    search_fields = (
        "employee__employee_number",
        "employee__first_name",
        "employee__last_name",
    )

    # Related objects are searchable instead of being represented by large dropdown lists
    autocomplete_fields = (
        "employee",
        "work_schedule",
        "corrected_by",
    )

    # date navigation
    date_hierarchy = "attendance_date"
