from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

# Employee Leave Management


# determines available leave types
class TimeOffType(models.Model):
    class Unit(models.TextChoices):
        DAYS = "DAYS", "Days"
        HOURS = "HOURS", "Hours"

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    unit = models.CharField(
        max_length=10,
        choices=Unit.choices,
        default=Unit.DAYS,
    )

    # tells if employees must have an allocation before requesting the leave
    requires_allocation = models.BooleanField(
        default=True,
    )

    # is it a paid or unpaid leave
    is_paid = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


# represents amount of specific leave type allocated to an employee for a defined period
# (allocations must be approved before being available)
class TimeOffAllocation(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="time_off_allocations",
    )

    time_off_type = models.ForeignKey(
        TimeOffType,
        on_delete=models.PROTECT,
        related_name="allocations",
    )

    allocation_year = models.PositiveIntegerField()

    allocated_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    used_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    valid_from = models.DateField()

    valid_until = models.DateField()

    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_time_off_allocations",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-allocation_year"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "time_off_type",
                    "allocation_year",
                ],
                name="unique_employee_timeoff_year",
            ),
        ]

        indexes = [
            models.Index(
                fields=["employee", "time_off_type"],
                name="allocation_employee_type_idx",
            ),
        ]

    # return leave balance for a particular leave type
    @property
    def remaining_days(self):
        return max(
            self.allocated_days - self.used_days,
            0,
        )

    def clean(self):
        if self.valid_until < self.valid_from:
            raise ValidationError("Allocation end date cannot be before start date.")

        if self.used_days > self.allocated_days:
            raise ValidationError("Used days cannot exceed allocated days.")

    def __str__(self):
        return (
            f"{self.employee.full_name} - "
            f"{self.time_off_type.name} - "
            f"{self.allocation_year}"
        )


# employees request to take time off
class TimeOffRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="time_off_requests",
    )

    time_off_type = models.ForeignKey(
        TimeOffType,
        on_delete=models.PROTECT,
        related_name="requests",
    )

    start_date = models.DateField()

    end_date = models.DateField()

    requested_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    reason = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_time_off_requests",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-start_date"]

        indexes = [
            models.Index(
                fields=["employee", "status"],
                name="timeoff_employee_status_idx",
            ),
            models.Index(
                fields=["start_date", "end_date"],
                name="timeoff_date_range_idx",
            ),
        ]

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")

        if self.requested_days <= 0:
            raise ValidationError("Requested days must be greater than zero.")

    def __str__(self):
        return (
            f"{self.employee.full_name} - "
            f"{self.time_off_type.name} - "
            f"{self.status}"
        )
