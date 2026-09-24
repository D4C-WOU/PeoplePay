from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from employees.models import Department, Employee, WorkSchedule
from users.models import User

from .models import (
    TimeOffAllocation,
    TimeOffRequest,
    TimeOffType,
)
from .services import (
    approve_time_off_request,
    get_available_allocation,
    reject_time_off_request,
)


class TimeOffServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create the reviewer who will approve requests
        cls.reviewer = User.objects.create_user(
            username="hr_reviewer",
            email="hr@test.com",
            password="TestPassword123",
        )

        # Create the employee requesting time off
        cls.employee_user = User.objects.create_user(
            username="timeoff_employee",
            email="employee@test.com",
            password="TestPassword123",
        )

        # Create the department required by the employee
        cls.department = Department.objects.create(
            code="TIME",
            name="Time Off Test Department",
        )

        # Create the work schedule required by the employee
        cls.schedule = WorkSchedule.objects.create(
            name="Time Off Test Schedule",
        )

        # Create the employee used by the tests
        cls.employee = Employee.objects.create(
            user=cls.employee_user,
            employee_number="TIME001",
            first_name="Time",
            last_name="Off",
            hire_date=date(2026, 1, 1),
            job_title="Software Engineer",
            department=cls.department,
            work_schedule=cls.schedule,
        )

        # Create an annual leave type requiring allocation
        cls.annual_leave = TimeOffType.objects.create(
            code="ANNUAL_TEST",
            name="Annual Leave",
            unit=TimeOffType.Unit.DAYS,
            requires_allocation=True,
            is_paid=True,
        )

        # Create a leave type that does not require allocation
        cls.unpaid_leave = TimeOffType.objects.create(
            code="UNPAID_TEST",
            name="Unpaid Leave",
            unit=TimeOffType.Unit.DAYS,
            requires_allocation=False,
            is_paid=False,
        )

    def create_allocation(self, allocated_days=10, used_days=0):
        # Create an approved annual leave allocation
        return TimeOffAllocation.objects.create(
            employee=self.employee,
            time_off_type=self.annual_leave,
            allocation_year=2026,
            allocated_days=allocated_days,
            used_days=used_days,
            status=TimeOffAllocation.Status.APPROVED,
            valid_from=date(2026, 1, 1),
            valid_until=date(2026, 12, 31),
        )

    def create_request(self, time_off_type=None, requested_days=2):
        # Create a pending time-off request
        return TimeOffRequest.objects.create(
            employee=self.employee,
            time_off_type=time_off_type or self.annual_leave,
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 11),
            requested_days=requested_days,
            reason="Personal leave",
            status=TimeOffRequest.Status.PENDING,
        )

    def test_finds_available_allocation(self):
        # Create an approved allocation with remaining balance
        allocation = self.create_allocation()

        # Ask the service for an allocation on the request date
        result = get_available_allocation(
            self.employee,
            self.annual_leave,
            date(2026, 9, 10),
        )

        # Confirm the correct allocation was returned
        self.assertEqual(result, allocation)

    def test_returns_none_without_approved_allocation(self):
        # Do not create an approved allocation

        # Ask the service for an allocation
        result = get_available_allocation(
            self.employee,
            self.annual_leave,
            date(2026, 9, 10),
        )

        # Confirm no allocation is available
        self.assertIsNone(result)

    def test_approval_deducts_allocation(self):
        # Create an allocation with ten available days
        allocation = self.create_allocation(allocated_days=10)

        # Create a request for two days
        request = self.create_request(requested_days=2)

        # Approve the request
        approve_time_off_request(request, self.reviewer)

        # Refresh the allocation from the database
        allocation.refresh_from_db()

        # Confirm two days were deducted
        self.assertEqual(allocation.used_days, 2)

        # Confirm the request was approved
        request.refresh_from_db()
        self.assertEqual(
            request.status,
            TimeOffRequest.Status.APPROVED,
        )

    def test_approval_fails_without_enough_balance(self):
        # Create an allocation with only one available day
        self.create_allocation(allocated_days=1)

        # Create a request for two days
        request = self.create_request(requested_days=2)

        # Confirm approval is rejected
        with self.assertRaises(ValidationError):
            approve_time_off_request(request, self.reviewer)

        # Confirm the request remains pending
        request.refresh_from_db()
        self.assertEqual(
            request.status,
            TimeOffRequest.Status.PENDING,
        )

    def test_rejection_does_not_change_allocation(self):
        # Create an allocation with ten available days
        allocation = self.create_allocation(allocated_days=10)

        # Create a request for two days
        request = self.create_request(requested_days=2)

        # Reject the request
        reject_time_off_request(request, self.reviewer)

        # Refresh the allocation from the database
        allocation.refresh_from_db()

        # Confirm the allocation was not changed
        self.assertEqual(allocation.used_days, 0)

        # Confirm the request was rejected
        request.refresh_from_db()
        self.assertEqual(
            request.status,
            TimeOffRequest.Status.REJECTED,
        )

    def test_already_processed_request_cannot_be_approved(self):
        # Create an allocation for the request
        self.create_allocation()

        # Create a pending request
        request = self.create_request()

        # Approve the request once
        approve_time_off_request(request, self.reviewer)

        # Confirm the same request cannot be approved again
        with self.assertRaises(ValidationError):
            approve_time_off_request(request, self.reviewer)

    def test_non_allocation_leave_can_be_approved(self):
        # Create an unpaid leave request that needs no allocation
        request = self.create_request(
            time_off_type=self.unpaid_leave,
            requested_days=2,
        )

        # Approve the request without an allocation
        approved_request, allocation = approve_time_off_request(
            request,
            self.reviewer,
        )

        # Confirm the request was approved
        self.assertEqual(
            approved_request.status,
            TimeOffRequest.Status.APPROVED,
        )

        # Confirm no allocation was used
        self.assertIsNone(allocation)
