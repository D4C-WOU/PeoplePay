from datetime import time

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import WorkSchedule, WorkScheduleDay
from .services import calculate_weekly_hours


class ScheduleServiceTests(TestCase):

    def test_calculates_weekly_hours_for_five_days(self):
        # Create a standard five-day work schedule
        schedule = WorkSchedule.objects.create(
            name="Five Day Test Schedule",
        )

        # Add five 8-hour days with a one-hour break
        for day in range(5):
            WorkScheduleDay.objects.create(
                work_schedule=schedule,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                break_minutes=60,
            )

        # Calculate the total weekly working hours
        result = calculate_weekly_hours(schedule)

        # Five seven-hour days should equal 35 hours
        self.assertEqual(result, 35)

    def test_calculates_weekly_hours_for_single_day(self):
        # Create a schedule with one working day
        schedule = WorkSchedule.objects.create(
            name="Single Day Test Schedule",
        )

        # Add a nine-to-five day with a one-hour break
        WorkScheduleDay.objects.create(
            work_schedule=schedule,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
            break_minutes=60,
        )

        # Calculate the weekly hours
        result = calculate_weekly_hours(schedule)

        # The day contains seven working hours
        self.assertEqual(result, 7)

    def test_handles_different_daily_hours(self):
        # Create a flexible work schedule
        schedule = WorkSchedule.objects.create(
            name="Flexible Test Schedule",
        )

        # Add a six-hour Monday
        WorkScheduleDay.objects.create(
            work_schedule=schedule,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(16, 0),
            break_minutes=60,
        )

        # Add an eight-hour Tuesday
        WorkScheduleDay.objects.create(
            work_schedule=schedule,
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(18, 0),
            break_minutes=60,
        )

        # Calculate the weekly hours
        result = calculate_weekly_hours(schedule)

        # Six hours plus eight hours equals fourteen hours
        self.assertEqual(result, 14)

    def test_rejects_invalid_working_time(self):
        # Create a schedule with invalid times
        schedule = WorkSchedule.objects.create(
            name="Invalid Time Schedule",
        )

        # End time is before start time
        WorkScheduleDay.objects.create(
            work_schedule=schedule,
            day_of_week=0,
            start_time=time(17, 0),
            end_time=time(9, 0),
            break_minutes=60,
        )

        # Confirm invalid working time is rejected
        with self.assertRaises(ValidationError):
            calculate_weekly_hours(schedule)

    def test_rejects_break_longer_than_working_time(self):
        # Create a schedule with an invalid break
        schedule = WorkSchedule.objects.create(
            name="Invalid Break Schedule",
        )

        # Break time is longer than the working period
        WorkScheduleDay.objects.create(
            work_schedule=schedule,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(10, 0),
            break_minutes=90,
        )

        # Confirm negative working time is rejected
        with self.assertRaises(ValidationError):
            calculate_weekly_hours(schedule)

    def test_empty_schedule_has_zero_hours(self):
        # Create a schedule without any working days
        schedule = WorkSchedule.objects.create(
            name="Empty Schedule",
        )

        # Calculate the weekly hours
        result = calculate_weekly_hours(schedule)

        # No configured days means zero working hours
        self.assertEqual(result, 0)
