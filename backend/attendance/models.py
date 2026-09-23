from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


# includes check-in/out, worked hours, status, and authorizzed corrections
class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        HALF_DAY = "HALF_DAY", "Half Day"
        LATE = "LATE", "Late"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        HOLIDAY = "HOLIDAY", "Holiday"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    # determines expected work hours
    work_schedule = models.ForeignKey(
        "employees.WorkSchedule",
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    attendance_date = models.DateField()

    check_in = models.DateTimeField(
        null=True,
        blank=True,
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True,
    )

    expected_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    worked_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
    )

    notes = models.TextField(
        blank=True,
    )

    corrected_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_corrections",
    )

    corrected_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-attendance_date"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "attendance_date",
                ],
                name="unique_employee_attendance_date",
            ),
        ]

        indexes = [
            models.Index(
                fields=["employee", "attendance_date"],
                name="attendance_employee_date_idx",
            ),
            models.Index(
                fields=["status", "attendance_date"],
                name="attendance_status_date_idx",
            ),
        ]

    def clean(self):
        if self.check_in and self.check_out:
            if self.check_out <= self.check_in:
                raise ValidationError("Check-out must be after check-in.")

    def __str__(self):
        return f"{self.employee.employee_number} - " f"{self.attendance_date}"
