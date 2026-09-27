from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError

from employees.models import WorkScheduleDay


def get_schedule_break_minutes(attendance):
    # Convert Python's weekday number into the schedule's weekday value
    weekday_map = {
        0: "MONDAY",
        1: "TUESDAY",
        2: "WEDNESDAY",
        3: "THURSDAY",
        4: "FRIDAY",
        5: "SATURDAY",
        6: "SUNDAY",
    }

    # Find the schedule day for this attendance date
    day_name = weekday_map[attendance.attendance_date.weekday()]

    schedule_day = WorkScheduleDay.objects.filter(
        work_schedule=attendance.work_schedule,
        day_of_week=day_name,
    ).first()

    # No configured schedule day means there is no break to subtract
    if not schedule_day:
        return 0

    return schedule_day.break_minutes


def calculate_attendance_hours(attendance):
    # Check that both check-in and check-out exist
    if not attendance.check_in or not attendance.check_out:
        raise ValidationError(
            "Check-in and check-out are required to calculate worked hours."
        )

    # Make sure check-out happens after check-in
    if attendance.check_out <= attendance.check_in:
        raise ValidationError("Check-out time must be after check-in time.")

    # Calculate elapsed time between check-in and check-out
    elapsed_seconds = (attendance.check_out - attendance.check_in).total_seconds()

    elapsed_minutes = Decimal(str(elapsed_seconds / 60))

    # Get the break configured for this employee's work schedule
    break_minutes = Decimal(str(get_schedule_break_minutes(attendance)))

    # Remove the scheduled break from the elapsed attendance time
    worked_minutes = max(
        Decimal("0"),
        elapsed_minutes - break_minutes,
    )

    # Convert worked minutes into hours
    worked_hours = (worked_minutes / Decimal("60")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    # Calculate overtime against expected schedule hours
    overtime_hours = worked_hours - attendance.expected_hours

    # Negative overtime is not stored
    if overtime_hours < 0:
        overtime_hours = Decimal("0.00")

    # Round overtime to two decimal places
    overtime_hours = overtime_hours.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    return worked_hours, overtime_hours


def update_attendance_hours(attendance):
    # Calculate worked and overtime hours
    worked_hours, overtime_hours = calculate_attendance_hours(attendance)

    # Store the calculated values
    attendance.worked_hours = worked_hours
    attendance.overtime_hours = overtime_hours

    # Save only the calculated fields
    attendance.save(
        update_fields=[
            "worked_hours",
            "overtime_hours",
        ]
    )

    return attendance
