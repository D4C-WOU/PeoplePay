from django.contrib import admin

from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):

    # most imp information when looking at contracts
    list_display = (
        "contract_number",
        "employee",
        "contract_type",
        "start_date",
        "end_date",
        "base_salary",
        "salary_structure",
        "status",
    )

    list_filter = (
        "contract_type",
        "status",
        "salary_structure",
    )

    # '__' tells django to follow a relationship
    # eg: emp__fname: search first name of an employee
    search_fields = (
        "contract_number",
        "employee__employee_number",
        "employee__first_name",
        "employee__last_name",
    )

    # represents relations with other models
    autocomplete_fields = (
        "employee",
        "salary_structure",
        "work_schedule",
    )

    date_hierarchy = "start_date"
