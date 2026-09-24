from django.contrib import admin

from .models import Department, Employee, WorkSchedule, WorkScheduleDay


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    # Helps HR quickly find departments by code or name.
    list_display = (
        "code",
        "name",
        "is_active",
    )

    list_filter = ("is_active",)

    search_fields = (
        "code",
        "name",
    )


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    # weekly_hours is calculated from the schedule's working days.
    list_display = (
        "name",
        "weekly_hours",
        "is_active",
    )

    list_filter = ("is_active",)

    search_fields = ("name",)


@admin.register(WorkScheduleDay)
class WorkScheduleDayAdmin(admin.ModelAdmin):
    # Shows the weekly working pattern used for employee schedules.
    list_display = (
        "work_schedule",
        "day_of_week",
        "start_time",
        "end_time",
        "break_minutes",
    )

    list_filter = (
        "day_of_week",
        "work_schedule",
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # Employee is the main HR record, so common HR filters are exposed here.
    list_display = (
        "employee_number",
        "full_name",
        "department",
        "job_title",
        "employee_type",
        "status",
        "hire_date",
    )

    list_filter = (
        "department",
        "employee_type",
        "status",
    )

    search_fields = (
        "employee_number",
        "first_name",
        "last_name",
        "job_title",
    )

    # Autocomplete keeps related employee records manageable as data grows.
    autocomplete_fields = (
        "user",
        "department",
        "manager",
        "work_schedule",
    )

    # full_name is calculated from first_name and last_name.
    readonly_fields = ("full_name",)
