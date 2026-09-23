from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


# represents reusable salary config, determines which rules are executed when payrun calculates employee payslips
class SalaryStructure(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    currency = models.CharField(
        max_length=3,
        default="INR",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


# represents 1 calculation rule inside a slaary structure
class SalaryRule(models.Model):
    class Category(models.TextChoices):
        BASIC = "BASIC", "Basic"  # Base salary
        ALLOWANCE = "ALLOWANCE", "Allowance"  # additional earnings
        GROSS = "GROSS", "Gross"  # total earnings before deductions
        DEDUCTION = "DEDUCTION", "Deduction"
        NET = "NET", "Net"  # final salary

    class CalculationType(models.TextChoices):
        FIXED = "FIXED", "Fixed Amount"
        PERCENTAGE = "PERCENTAGE", "Percentage"
        FORMULA = "FORMULA", "Formula"

    salary_structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.CASCADE,
        related_name="rules",
    )

    code = models.CharField(
        max_length=50,
    )

    name = models.CharField(
        max_length=150,
    )

    # payroll category to which this rule belongs
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )

    # determines order in which this rule is evaluated
    sequence = models.PositiveIntegerField(
        default=10,
    )

    # determines how the rule calculates its result
    calculation_type = models.CharField(
        max_length=20,
        choices=CalculationType.choices,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    formula = models.TextField(
        blank=True,
    )

    based_on = models.CharField(
        max_length=50,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["sequence", "id"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "salary_structure",
                    "code",
                ],
                name="unique_salary_rule_code",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "salary_structure",
                    "sequence",
                ],
                name="salary_rule_sequence_idx",
            ),
        ]

    def clean(self):
        if self.calculation_type == self.CalculationType.FIXED:
            if self.amount is None:
                raise ValidationError("Fixed salary rules require an amount.")

        elif self.calculation_type == self.CalculationType.PERCENTAGE:
            if self.percentage is None:
                raise ValidationError("Percentage salary rules require a percentage.")

            if self.percentage > 100:
                raise ValidationError("Percentage cannot exceed 100.")

            if not self.based_on:
                raise ValidationError("Percentage rules require a base rule code.")

        elif self.calculation_type == self.CalculationType.FORMULA:
            if not self.formula.strip():
                raise ValidationError("Formula salary rules require a formula.")

    def __str__(self):
        return f"{self.salary_structure.code} - " f"{self.sequence} - " f"{self.code}"


# represents 1 payroll processing cycle for a defined period
# A Payrun groups the employees being paid, the salary structure used for calculation,
# the payroll period, and the resulting
# payslips and payroll totals.
class Payrun(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        COMPUTED = "COMPUTED", "Computed"
        VALIDATED = "VALIDATED", "Validated"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    name = models.CharField(
        max_length=150,
    )

    # rules of ts will be used to calculate payslips in the payrun
    salary_structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.PROTECT,
        related_name="payruns",
    )

    period_start = models.DateField()

    period_end = models.DateField()

    payment_date = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    selected_employees = models.ManyToManyField(
        "employees.Employee",
        related_name="selected_payruns",
        blank=True,
    )

    employee_count = models.PositiveIntegerField(
        default=0,
    )

    # Aggregated gross salary for the Payrun
    gross_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    deduction_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    net_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-period_start", "-created_at"]

        indexes = [
            models.Index(
                fields=["period_start", "period_end"],
                name="payrun_period_idx",
            ),
            models.Index(
                fields=["status"],
                name="payrun_status_idx",
            ),
        ]

    def clean(self):
        if self.period_end < self.period_start:
            raise ValidationError("Payrun end date cannot be before start date.")

        if self.payment_date and self.payment_date < self.period_end:
            raise ValidationError(
                "Payment date cannot be before the payrun period ends."
            )

    def __str__(self):
        return self.name


# Represents the payroll result for one employee within a Payrun.
# connects the employee, applicable employment contract, salary structure, payroll period, and calculated salary totals
class Payslip(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        FINALIZED = "FINALIZED", "Finalized"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    # payrun to which this payslip belongs
    payrun = models.ForeignKey(
        Payrun,
        on_delete=models.PROTECT,
        related_name="payslips",
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="payslips",
    )

    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.PROTECT,
        related_name="payslips",
    )

    salary_structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.PROTECT,
        related_name="payslips",
    )

    period_start = models.DateField()

    period_end = models.DateField()

    worked_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
    )

    # employee identifier captured at payroll
    employee_number_snapshot = models.CharField(
        max_length=50,
    )

    employee_name_snapshot = models.CharField(
        max_length=200,
    )

    currency = models.CharField(
        max_length=3,
        default="INR",
    )

    gross_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    deduction_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    generated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-period_start", "employee_number_snapshot"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "payrun",
                    "employee",
                ],
                name="unique_employee_payslip_per_payrun",
            ),
        ]

        indexes = [
            models.Index(
                fields=["employee", "period_start"],
                name="payslip_employee_period_idx",
            ),
            models.Index(
                fields=["status"],
                name="payslip_status_idx",
            ),
        ]

    def clean(self):
        if self.period_end < self.period_start:
            raise ValidationError("Payslip end date cannot be before start date.")

        if self.gross_amount < 0:
            raise ValidationError("Gross amount cannot be negative.")

        if self.deduction_amount < 0:
            raise ValidationError("Deduction amount cannot be negative.")

    def __str__(self):
        return (
            f"{self.employee_name_snapshot} - "
            f"{self.period_start} to {self.period_end}"
        )


# Represents one calculated salary-rule result on a payslip.


class PayslipLine(models.Model):
    payslip = models.ForeignKey(
        Payslip,
        on_delete=models.CASCADE,
        related_name="lines",
    )

    salary_rule = models.ForeignKey(
        SalaryRule,
        on_delete=models.PROTECT,
        related_name="payslip_lines",
    )

    # snapshot of the salary rule code used during calculation
    code = models.CharField(
        max_length=50,
    )

    name = models.CharField(
        max_length=150,
    )

    # payroll category
    category = models.CharField(
        max_length=20,
    )

    # calculation order used by salary engine
    sequence = models.PositiveIntegerField()

    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    calculated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["sequence", "id"]

        indexes = [
            models.Index(
                fields=["payslip", "sequence"],
                name="payslip_line_sequence_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.payslip.employee_name_snapshot} - "
            f"{self.code} - "
            f"{self.calculated_amount}"
        )
