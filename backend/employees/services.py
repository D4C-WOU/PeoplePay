from datetime import datetime, date

from django.core.exceptions import ValidationError

from .models import WorkSchedule, WorkScheduleDay


# represents schedule services
def calculate_weekly_hours(schedule: WorkSchedule) -> float:
    # Get all working days for this schedule
    schedule_days = WorkScheduleDay.objects.filter(work_schedule=schedule)

    total_minutes = 0

    # Calculate worked time for each day
    for schedule_day in schedule_days:
        start = datetime.combine(date.today(), schedule_day.start_time)
        end = datetime.combine(date.today(), schedule_day.end_time)

        # Make sure the working period is valid
        if end <= start:
            raise ValidationError(
                f"End time must be after start time for "
                f"{schedule_day.get_day_of_week_display()}."
            )

        # Remove the configured break from the day's duration
        worked_minutes = (
            (end - start).total_seconds() / 60
        ) - schedule_day.break_minutes

        # Prevent negative working time
        if worked_minutes < 0:
            raise ValidationError(
                f"Break time cannot exceed working time for "
                f"{schedule_day.get_day_of_week_display()}."
            )

        total_minutes += worked_minutes

    # Convert total minutes to weekly hours
    return round(total_minutes / 60, 2)
