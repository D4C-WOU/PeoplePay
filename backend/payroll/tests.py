from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import SalaryRule, SalaryStructure
from .services import calculate_salary_rules


class SalaryRuleEngineTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create the salary structure used by all tests
        cls.structure = SalaryStructure.objects.create(
            code="TEST-MONTHLY",
            name="Test Monthly Salary",
        )

    def test_calculates_fixed_rule(self):
        # Create a fixed salary rule
        rule = SalaryRule.objects.create(
            salary_structure=self.structure,
            code="BONUS",
            name="Bonus",
            category=SalaryRule.Category.ALLOWANCE,
            sequence=10,
            calculation_type=SalaryRule.CalculationType.FIXED,
            amount=Decimal("5000.00"),
        )

        # Calculate the salary rules
        result = calculate_salary_rules(
            self.structure,
            Decimal("60000.00"),
        )

        # Confirm the fixed amount was returned
        self.assertEqual(
            result[rule.code]["amount"],
            Decimal("5000.00"),
        )

    def test_calculates_percentage_rule(self):
        # Create a percentage rule based on BASIC
        rule = SalaryRule.objects.create(
            salary_structure=self.structure,
            code="HRA",
            name="House Rent Allowance",
            category=SalaryRule.Category.ALLOWANCE,
            sequence=10,
            calculation_type=SalaryRule.CalculationType.PERCENTAGE,
            percentage=Decimal("20.00"),
            based_on="BASIC",
        )

        # Calculate the salary rules
        result = calculate_salary_rules(
            self.structure,
            Decimal("60000.00"),
        )

        # Confirm 20 percent of 60000 equals 12000
        self.assertEqual(
            result[rule.code]["amount"],
            Decimal("12000.00"),
        )

    def test_calculates_formula_rule_using_previous_rule(self):
        # Create an allowance based on BASIC
        SalaryRule.objects.create(
            salary_structure=self.structure,
            code="HRA",
            name="House Rent Allowance",
            category=SalaryRule.Category.ALLOWANCE,
            sequence=10,
            calculation_type=SalaryRule.CalculationType.PERCENTAGE,
            percentage=Decimal("20.00"),
            based_on="BASIC",
        )

        # Create a formula rule using BASIC and HRA
        gross_rule = SalaryRule.objects.create(
            salary_structure=self.structure,
            code="GROSS",
            name="Gross Salary",
            category=SalaryRule.Category.GROSS,
            sequence=20,
            calculation_type=SalaryRule.CalculationType.FORMULA,
            formula="BASIC + HRA",
        )

        # Calculate the salary rules
        result = calculate_salary_rules(
            self.structure,
            Decimal("60000.00"),
        )

        # Confirm gross salary equals basic plus HRA
        self.assertEqual(
            result[gross_rule.code]["amount"],
            Decimal("72000.00"),
        )

    def test_calculates_multiple_rules_in_sequence(self):
        # Create HRA using 20 percent of BASIC
        SalaryRule.objects.create(
            salary_structure=self.structure,
            code="HRA",
            name="House Rent Allowance",
            category=SalaryRule.Category.ALLOWANCE,
            sequence=10,
            calculation_type=SalaryRule.CalculationType.PERCENTAGE,
            percentage=Decimal("20.00"),
            based_on="BASIC",
        )

        # Create gross salary from BASIC and HRA
        SalaryRule.objects.create(
            salary_structure=self.structure,
            code="GROSS",
            name="Gross Salary",
            category=SalaryRule.Category.GROSS,
            sequence=20,
            calculation_type=SalaryRule.CalculationType.FORMULA,
            formula="BASIC + HRA",
        )

        # Create PF using 12 percent of BASIC
        SalaryRule.objects.create(
            salary_structure=self.structure,
            code="PF",
            name="Provident Fund",
            category=SalaryRule.Category.DEDUCTION,
            sequence=30,
            calculation_type=SalaryRule.CalculationType.PERCENTAGE,
            percentage=Decimal("12.00"),
            based_on="BASIC",
        )

        # Create net salary from GROSS minus PF
        SalaryRule.objects.create(
            salary_structure=self.structure,
            code="NET",
            name="Net Salary",
            category=SalaryRule.Category.NET,
            sequence=40,
            calculation_type=SalaryRule.CalculationType.FORMULA,
            formula="GROSS - PF",
        )

        # Calculate the complete salary structure
        result = calculate_salary_rules(
            self.structure,
            Decimal("60000.00"),
        )

        # Confirm the final net salary
        self.assertEqual(
            result["NET"]["amount"],
            Decimal("64800.00"),
        )

    def test_rejects_missing_percentage_dependency(self):
        # Create a percentage rule without a base rule
        SalaryRule.objects.create(
            salary_structure=self.structure,
            code="HRA",
            name="House Rent Allowance",
            category=SalaryRule.Category.ALLOWANCE,
            sequence=10,
            calculation_type=SalaryRule.CalculationType.PERCENTAGE,
            percentage=Decimal("20.00"),
            based_on="MISSING",
        )

        # Confirm the missing dependency is rejected
        with self.assertRaises(ValidationError):
            calculate_salary_rules(
                self.structure,
                Decimal("60000.00"),
            )

    def test_rejects_formula_using_future_rule(self):
        # Create a formula that references a rule not calculated yet
        SalaryRule.objects.create(
            salary_structure=self.structure,
            code="NET",
            name="Net Salary",
            category=SalaryRule.Category.NET,
            sequence=10,
            calculation_type=SalaryRule.CalculationType.FORMULA,
            formula="BASIC - PF",
        )

        # Confirm the invalid dependency is rejected
        with self.assertRaises(ValidationError):
            calculate_salary_rules(
                self.structure,
                Decimal("60000.00"),
            )

    def test_rejects_unsupported_formula_characters(self):
        # Create a formula containing unsupported characters
        SalaryRule.objects.create(
            salary_structure=self.structure,
            code="BAD",
            name="Invalid Formula",
            category=SalaryRule.Category.ALLOWANCE,
            sequence=10,
            calculation_type=SalaryRule.CalculationType.FORMULA,
            formula="BASIC + __import__('os')",
        )

        # Confirm unsafe formula content is rejected
        with self.assertRaises(ValidationError):
            calculate_salary_rules(
                self.structure,
                Decimal("60000.00"),
            )
