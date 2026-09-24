from django.contrib import admin

from .models import (
    Payslip,
    PayslipLine,
    Payrun,
    SalaryRule,
    SalaryStructure,
)


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    # Salary structures define which rules are used during payroll.
    list_display = (
        "code",
        "name",
        "currency",
        "is_active",
    )

    list_filter = (
        "is_active",
        "currency",
    )

    search_fields = (
        "code",
        "name",
    )


@admin.register(SalaryRule)
class SalaryRuleAdmin(admin.ModelAdmin):
    # Rules are ordered because later rules can depend on earlier results.
    list_display = (
        "code",
        "name",
        "salary_structure",
        "category",
        "sequence",
        "calculation_type",
        "is_active",
    )

    list_filter = (
        "category",
        "calculation_type",
        "is_active",
        "salary_structure",
    )

    search_fields = (
        "code",
        "name",
        "salary_structure__code",
        "salary_structure__name",
    )

    autocomplete_fields = ("salary_structure",)

    ordering = (
        "salary_structure",
        "sequence",
    )


@admin.register(Payrun)
class PayrunAdmin(admin.ModelAdmin):
    # A payrun groups employees and payslips for one payroll period.
    list_display = (
        "name",
        "salary_structure",
        "period_start",
        "period_end",
        "status",
        "employee_count",
        "gross_total",
        "deduction_total",
        "net_total",
    )

    list_filter = (
        "status",
        "salary_structure",
        "period_start",
    )

    search_fields = ("name",)

    autocomplete_fields = ("salary_structure",)

    # Makes selecting multiple employees easier when creating a payrun.
    filter_horizontal = ("selected_employees",)

    date_hierarchy = "period_start"


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    # Payslips preserve the payroll result for each employee and period.
    list_display = (
        "employee",
        "payrun",
        "period_start",
        "period_end",
        "gross_amount",
        "deduction_amount",
        "net_amount",
        "status",
    )

    list_filter = (
        "status",
        "salary_structure",
        "period_start",
    )

    search_fields = (
        "employee__employee_number",
        "employee__first_name",
        "employee__last_name",
        "employee_name_snapshot",
    )

    autocomplete_fields = (
        "payrun",
        "employee",
        "contract",
        "salary_structure",
    )

    date_hierarchy = "period_start"


@admin.register(PayslipLine)
class PayslipLineAdmin(admin.ModelAdmin):
    # Each line shows the result of one salary rule on a payslip.
    list_display = (
        "payslip",
        "code",
        "name",
        "category",
        "sequence",
        "calculated_amount",
    )

    list_filter = ("category",)

    search_fields = (
        "code",
        "name",
        "payslip__employee__employee_number",
    )

    autocomplete_fields = (
        "payslip",
        "salary_rule",
    )

    ordering = (
        "payslip",
        "sequence",
    )
