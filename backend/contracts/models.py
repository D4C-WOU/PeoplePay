from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

# historic records and period specific applicability


# Only the contract applicable to the Payrun period should be used
class Contract(models.Model):
    class ContractType(models.TextChoices):
        PERMANENT = "PERMANENT", "Permanent"
        FIXED_TERM = "FIXED_TERM", "Fixed Term"  # employee valid for 1 project
        PART_TIME = "PART_TIME", "Part Time"  # employee valid for part time =
        CONTRACT = "CONTRACT", "Contract"  # employee valid till the  contract duration

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"  # contract created but not active
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        TERMINATED = "TERMINATED", "Terminated"

    # employee to whom this contract belongs
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="contracts",
    )

    # salary structure rules associated with this contract
    salary_structure = models.ForeignKey(
        "payroll.SalaryStructure",
        on_delete=models.PROTECT,
        related_name="contracts",
    )

    work_schedule = models.ForeignKey(
        "employees.WorkSchedule",
        on_delete=models.PROTECT,
        related_name="contracts",
    )

    # unique identifier
    contract_number = models.CharField(
        max_length=50,
        unique=True,
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    contract_type = models.CharField(
        max_length=20,
        choices=ContractType.choices,
    )

    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    currency = models.CharField(
        max_length=3,
        default="INR",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-start_date"]

        indexes = [
            models.Index(
                fields=["employee", "start_date"],
                name="contract_employee_start_idx",
            ),
            models.Index(
                fields=["status"],
                name="contract_status_idx",
            ),
        ]

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("Contract end date cannot be before start date.")

        overlapping_contracts = Contract.objects.filter(
            employee=self.employee,
        ).exclude(
            pk=self.pk,
        )

        for contract in overlapping_contracts:
            existing_end = contract.end_date

            if existing_end is None:
                existing_end = self.start_date

            current_end = self.end_date

            if current_end is None:
                current_end = contract.start_date

            if self.start_date <= existing_end and contract.start_date <= current_end:
                raise ValidationError("Employee cannot have overlapping contracts.")

    def __str__(self):
        return f"{self.contract_number} - {self.employee.full_name}"
