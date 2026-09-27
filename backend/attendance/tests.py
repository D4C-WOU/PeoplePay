from datetime import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from attendance.services import calculate_attendance_hours
from attendance.models import AttendanceRecord
from employees.models import Employee, WorkSchedule, WorkScheduleDay


@pytest.mark.django_db
def test_full_day_calculates_worked_hours_without_overtime():
    # Create a schedule with a one-hour break
    schedule = WorkSchedule.objects.create(
        name="Test Schedule",
    )

    WorkScheduleDay.objects.create(
        work_schedule=schedule,
        day_of_week="TUESDAY",
        start_time="09:00",
        end_time="17:30",
        break_minutes=60,
    )

    # Create an attendance record for Tuesday
    attendance = AttendanceRecord(
        work_schedule=schedule,
        attendance_date=datetime(2026, 9, 1).date(),
        check_in=timezone.make_aware(datetime(2026, 9, 1, 9, 0)),
        check_out=timezone.make_aware(datetime(2026, 9, 1, 17, 30)),
        expected_hours=Decimal("7.50"),
    )

    # Calculate the attendance hours
    worked_hours, overtime_hours = calculate_attendance_hours(attendance)

    # 8.5 elapsed hours - 1 hour break = 7.5 worked
    assert worked_hours == Decimal("7.50")

    # Worked hours equal expected hours
    assert overtime_hours == Decimal("0.00")


@pytest.mark.django_db
def test_late_arrival_calculates_lower_worked_hours():
    # Create a schedule with a one-hour break
    schedule = WorkSchedule.objects.create(
        name="Late Test Schedule",
    )

    WorkScheduleDay.objects.create(
        work_schedule=schedule,
        day_of_week="TUESDAY",
        start_time="09:00",
        end_time="17:30",
        break_minutes=60,
    )

    # Employee arrives thirty minutes late
    attendance = AttendanceRecord(
        work_schedule=schedule,
        attendance_date=datetime(2026, 9, 1).date(),
        check_in=timezone.make_aware(datetime(2026, 9, 1, 9, 30)),
        check_out=timezone.make_aware(datetime(2026, 9, 1, 17, 30)),
        expected_hours=Decimal("7.50"),
    )

    # Calculate the attendance hours
    worked_hours, overtime_hours = calculate_attendance_hours(attendance)

    # 8 hours elapsed - 1 hour break = 7 hours worked
    assert worked_hours == Decimal("7.00")

    # No overtime when worked hours are below expected hours
    assert overtime_hours == Decimal("0.00")


@pytest.mark.django_db
def test_overtime_is_calculated_after_schedule_break():
    # Create a schedule with a one-hour break
    schedule = WorkSchedule.objects.create(
        name="Overtime Test Schedule",
    )

    WorkScheduleDay.objects.create(
        work_schedule=schedule,
        day_of_week="TUESDAY",
        start_time="09:00",
        end_time="17:30",
        break_minutes=60,
    )

    # Employee works until 7 PM
    attendance = AttendanceRecord(
        work_schedule=schedule,
        attendance_date=datetime(2026, 9, 1).date(),
        check_in=timezone.make_aware(datetime(2026, 9, 1, 9, 0)),
        check_out=timezone.make_aware(datetime(2026, 9, 1, 19, 0)),
        expected_hours=Decimal("7.50"),
    )

    # Calculate the attendance hours
    worked_hours, overtime_hours = calculate_attendance_hours(attendance)

    # 10 hours elapsed - 1 hour break = 9 hours worked
    assert worked_hours == Decimal("9.00")

    # 9 worked - 7.5 expected = 1.5 overtime
    assert overtime_hours == Decimal("1.50")


@pytest.mark.django_db
def test_missing_check_in_or_check_out_is_rejected():
    # Create a schedule
    schedule = WorkSchedule.objects.create(
        name="Validation Test Schedule",
    )

    # Create an incomplete attendance record
    attendance = AttendanceRecord(
        work_schedule=schedule,
        attendance_date=datetime(2026, 9, 1).date(),
        check_in=None,
        check_out=None,
        expected_hours=Decimal("7.50"),
    )

    # Calculation should fail because times are missing
    with pytest.raises(ValidationError):
        calculate_attendance_hours(attendance)


@pytest.mark.django_db
def test_check_out_before_check_in_is_rejected():
    # Create a schedule
    schedule = WorkSchedule.objects.create(
        name="Invalid Time Schedule",
    )

    # Create an attendance record with invalid times
    attendance = AttendanceRecord(
        work_schedule=schedule,
        attendance_date=datetime(2026, 9, 1).date(),
        check_in=timezone.make_aware(datetime(2026, 9, 1, 17, 0)),
        check_out=timezone.make_aware(datetime(2026, 9, 1, 9, 0)),
        expected_hours=Decimal("7.50"),
    )

    # Calculation should reject the invalid time range
    with pytest.raises(ValidationError):
        calculate_attendance_hours(attendance)
