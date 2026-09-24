from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from employees.models import Department, Employee, WorkSchedule, WorkScheduleDay
from payroll.models import SalaryStructure
from users.models import User

from .models import Contract
from .services import get_applicable_contract


class ContractServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a test user for the employee
        cls.user = User.objects.create_user(
            username="contract_test_user",
            email="contract@test.com",
            password="TestPassword123",
        )

        # Create the department used by the test employee
        cls.department = Department.objects.create(
            code="TEST",
            name="Test Department",
        )

        # Create a work schedule required by the employee
        cls.schedule = WorkSchedule.objects.create(
            name="Test Schedule",
        )

        # Add one working day to the test schedule
        WorkScheduleDay.objects.create(
            work_schedule=cls.schedule,
            day_of_week=0,
            start_time="09:00",
            end_time="17:00",
            break_minutes=60,
        )

        # Create the employee used in all contract tests
        cls.employee = Employee.objects.create(
            user=cls.user,
            employee_number="TEST001",
            first_name="Test",
            last_name="Employee",
            hire_date=date(2026, 1, 1),
            job_title="Software Engineer",
            department=cls.department,
            work_schedule=cls.schedule,
        )

        # Create the salary structure required by contracts
        cls.salary_structure = SalaryStructure.objects.create(
            code="TEST-MONTHLY",
            name="Test Monthly Salary",
        )

    def test_returns_contract_covering_payroll_period(self):
        # Create a contract covering the September payroll period
        contract = Contract.objects.create(
            employee=self.employee,
            salary_structure=self.salary_structure,
            work_schedule=self.schedule,
            contract_number="TEST-CONTRACT-001",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            base_salary=60000,
            status=Contract.Status.ACTIVE,
        )

        # Ask the service to find the applicable September contract
        result = get_applicable_contract(
            self.employee,
            date(2026, 9, 1),
            date(2026, 9, 30),
        )

        # Confirm the correct contract was returned
        self.assertEqual(result, contract)

    def test_returns_open_ended_contract(self):
        # Create a contract with no end date
        contract = Contract.objects.create(
            employee=self.employee,
            salary_structure=self.salary_structure,
            work_schedule=self.schedule,
            contract_number="TEST-CONTRACT-002",
            start_date=date(2026, 1, 1),
            end_date=None,
            base_salary=60000,
            status=Contract.Status.ACTIVE,
        )

        # Ask the service to find the September contract
        result = get_applicable_contract(
            self.employee,
            date(2026, 9, 1),
            date(2026, 9, 30),
        )

        # Confirm the open-ended contract is accepted
        self.assertEqual(result, contract)

    def test_rejects_period_outside_contract(self):
        # Create a contract that ends before the payroll period
        Contract.objects.create(
            employee=self.employee,
            salary_structure=self.salary_structure,
            work_schedule=self.schedule,
            contract_number="TEST-CONTRACT-003",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 8, 31),
            base_salary=60000,
            status=Contract.Status.ACTIVE,
        )

        # Confirm payroll cannot find a valid September contract
        with self.assertRaises(ValidationError):
            get_applicable_contract(
                self.employee,
                date(2026, 9, 1),
                date(2026, 9, 30),
            )

    def test_rejects_invalid_payroll_period(self):
        # Give the service an invalid date range
        with self.assertRaises(ValidationError):
            get_applicable_contract(
                self.employee,
                date(2026, 9, 30),
                date(2026, 9, 1),
            )
