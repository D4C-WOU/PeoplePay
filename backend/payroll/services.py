from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError

from .models import SalaryRule


def calculate_salary_rules(salary_structure, base_salary):
    # Convert the salary to Decimal for accurate money calculations
    base_salary = Decimal(str(base_salary)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    # Load active rules in their configured execution order
    rules = SalaryRule.objects.filter(
        salary_structure=salary_structure,
        is_active=True,
    ).order_by("sequence", "id")

    results = {}
    calculated_values = {}

    # Calculate each salary rule in sequence
    for rule in rules:
        amount = Decimal("0.00")

        # Fixed rules use their configured amount
        if rule.calculation_type == SalaryRule.CalculationType.FIXED:
            amount = rule.amount or Decimal("0.00")

        # Percentage rules use their configured base rule
        elif rule.calculation_type == SalaryRule.CalculationType.PERCENTAGE:
            if not rule.based_on:
                raise ValidationError(
                    f"Salary rule {rule.code} requires a based_on value."
                )

            base_value = get_rule_value(
                rule.based_on,
                base_salary,
                calculated_values,
            )

            amount = (base_value * (rule.percentage or Decimal("0.00"))) / Decimal(
                "100"
            )

        # Formula rules use previously calculated rule values
        elif rule.calculation_type == SalaryRule.CalculationType.FORMULA:
            if not rule.formula:
                raise ValidationError(f"Salary rule {rule.code} requires a formula.")

            amount = calculate_formula(
                rule.formula,
                base_salary,
                calculated_values,
            )

        # Round every salary rule to two decimal places
        amount = amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        # Store the result using the salary rule code
        calculated_values[rule.code] = amount

        results[rule.code] = {
            "rule": rule,
            "amount": amount,
        }

    return results


def get_rule_value(rule_code, base_salary, calculated_values):
    # BASIC always represents the contract base salary
    if rule_code == "BASIC":
        return base_salary

    # Other values must already have been calculated
    if rule_code not in calculated_values:
        raise ValidationError(f"Salary rule {rule_code} has not been calculated yet.")

    return calculated_values[rule_code]


def calculate_formula(formula, base_salary, calculated_values):
    # Allow only basic arithmetic operators and salary rule codes
    allowed_characters = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "._ +-*()/"
    )

    if any(character not in allowed_characters for character in formula):
        raise ValidationError("Formula contains unsupported characters.")

    expression = formula

    # Replace BASIC and calculated rule codes with their values
    values = {
        "BASIC": base_salary,
        **calculated_values,
    }

    for code, value in sorted(
        values.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        expression = expression.replace(code, str(value))

    try:
        # Evaluate only the restricted arithmetic expression
        result = eval(
            expression,
            {"__builtins__": {}},
            {},
        )
    except Exception as exc:
        raise ValidationError(f"Invalid salary rule formula: {formula}") from exc

    return Decimal(str(result))
