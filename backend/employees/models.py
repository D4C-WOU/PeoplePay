from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

# contains Department, WorkSchedule, WorkScheduleDay, Employee details


# department within the company
class Department(models.Model):
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

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


# reusable schedule for work which includes WorkScheduleDay
class WorkSchedule(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]

    @property
    def weekly_hours(self):
        """
        Calculate total weekly working hours from the configured
        schedule days.

        Example:
        Monday-Friday, 9:00-17:30, 60 minute break
        = 7.5 hours/day × 5 = 37.5 hours/week
        """
        total_hours = 0.0

        for day in self.days.all():
            start = datetime.combine(
                datetime.today(),
                day.start_time,
            )

            end = datetime.combine(
                datetime.today(),
                day.end_time,
            )

            duration = end - start
            duration -= timedelta(minutes=day.break_minutes)

            total_hours += duration.total_seconds() / 3600

        return round(total_hours, 2)

    def __str__(self):
        return self.name


# weekly work hours are calculated from these days
class WorkScheduleDay(models.Model):
    class DayOfWeek(models.TextChoices):
        MONDAY = "MONDAY", "Monday"
        TUESDAY = "TUESDAY", "Tuesday"
        WEDNESDAY = "WEDNESDAY", "Wednesday"
        THURSDAY = "THURSDAY", "Thursday"
        FRIDAY = "FRIDAY", "Friday"
        SATURDAY = "SATURDAY", "Saturday"
        SUNDAY = "SUNDAY", "Sunday"

    work_schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.CASCADE,
        related_name="days",
    )

    day_of_week = models.CharField(
        max_length=10,
        choices=DayOfWeek.choices,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    # break  duration deducted during actual work hours
    break_minutes = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "work_schedule",
                    "day_of_week",
                ],
                name="unique_schedule_day",
            ),
        ]

        ordering = ["day_of_week"]

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be later than start time.")

        total_minutes = (
            self.end_time.hour * 60
            + self.end_time.minute
            - (self.start_time.hour * 60 + self.start_time.minute)
        )

        if self.break_minutes > total_minutes:
            raise ValidationError("Break time cannot exceed the working duration.")

    def __str__(self):
        return f"{self.work_schedule.name} - {self.day_of_week}"


# central HR record of every employee in a company
class Employee(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        TERMINATED = "TERMINATED", "Terminated"

    class EmployeeType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"
        INTERN = "INTERN", "Intern"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )

    employee_number = models.CharField(
        max_length=50,
        unique=True,
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    hire_date = models.DateField()

    termination_date = models.DateField(
        null=True,
        blank=True,
    )

    job_title = models.CharField(
        max_length=150,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
    )
    # optional manager of the employee
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members",
    )

    work_schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.PROTECT,
        related_name="employees",
    )

    # HR can filter and report employee via ts(classficiation method)
    employee_type = models.CharField(
        max_length=20,
        choices=EmployeeType.choices,
        default=EmployeeType.FULL_TIME,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    address = models.TextField(
        blank=True,
    )

    # emergency contact infofor HR
    emergency_contact_name = models.CharField(
        max_length=150,
        blank=True,
    )

    emergency_contact_phone = models.CharField(
        max_length=30,
        blank=True,
    )

    # bank details for payroll processing
    bank_name = models.CharField(
        max_length=255,
        blank=True,
    )

    bank_account_number = models.CharField(
        max_length=100,
        blank=True,
    )

    bank_ifsc = models.CharField(
        max_length=20,
        blank=True,
    )

    class Meta:
        ordering = ["employee_number"]

        indexes = [
            models.Index(
                fields=["department", "status"],
                name="employee_dept_status_idx",
            ),
            models.Index(
                fields=["employee_type"],
                name="employee_type_idx",
            ),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.employee_number} - {self.full_name}"
