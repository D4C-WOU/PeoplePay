import ast
from decimal import Decimal
from typing import Any

from app.models.salary_rule import (
    CalculationType,
    SalaryRule,
    SalaryRuleCategory,
)
from app.utils.calculations import money

_ALLOWED_BINOPS = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
)

_ALLOWED_UNARY = (
    ast.UAdd,
    ast.USub,
)

_ALLOWED_NAMES = {
    "base_salary",
    "gross",
    "total_earnings",
    "total_deductions",
    "total_tax",
    "worked_days",
    "overtime_hours",
}


def _safe_formula(
    formula: str,
    variables: dict[str, Decimal],
) -> Decimal:
    if not formula or not formula.strip():
        raise ValueError("Formula cannot be empty")

    try:
        tree = ast.parse(formula, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Invalid salary formula") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Expression):
            continue

        if isinstance(node, ast.Constant):
            # Only integer constants are allowed.
            # This avoids Decimal/float arithmetic problems.
            if not isinstance(node.value, int) or isinstance(node.value, bool):
                raise ValueError("Only integer numeric constants are allowed")
            continue

        if isinstance(node, ast.Name):
            if node.id not in _ALLOWED_NAMES:
                raise ValueError(f"Unsupported formula variable: {node.id}")
            continue

        if isinstance(node, ast.BinOp):
            if not isinstance(node.op, _ALLOWED_BINOPS):
                raise ValueError("Unsupported formula operator")
            continue

        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, _ALLOWED_UNARY):
                raise ValueError("Unsupported formula operator")
            continue

        if isinstance(node, ast.Load):
            continue

        raise ValueError("Unsupported formula expression")

    safe_vars = {key: Decimal(str(value)) for key, value in variables.items()}

    try:
        compiled = compile(
            tree,
            "<salary_formula>",
            "eval",
        )

        result = eval(
            compiled,
            {"__builtins__": {}},
            safe_vars,
        )

        return Decimal(str(result))

    except ZeroDivisionError as exc:
        raise ValueError("Salary formula cannot divide by zero") from exc

    except (ArithmeticError, ValueError, TypeError) as exc:
        raise ValueError("Invalid salary formula calculation") from exc


def calculate_salary(
    base_salary: Decimal,
    rules: list[SalaryRule],
    *,
    worked_days: Decimal = Decimal("0"),
    overtime_hours: Decimal = Decimal("0"),
) -> dict[str, Any]:

    base_salary = money(base_salary)

    worked_days = Decimal(str(worked_days))
    overtime_hours = Decimal(str(overtime_hours))

    if base_salary < Decimal("0"):
        raise ValueError("Base salary cannot be negative")

    if worked_days < Decimal("0"):
        raise ValueError("Worked days cannot be negative")

    if overtime_hours < Decimal("0"):
        raise ValueError("Overtime hours cannot be negative")

    values = {
        "base_salary": base_salary,
        "gross": base_salary,
        "total_earnings": base_salary,
        "total_deductions": Decimal("0"),
        "total_tax": Decimal("0"),
        "worked_days": worked_days,
        "overtime_hours": overtime_hours,
    }

    lines = []

    active_rules = sorted(
        (rule for rule in rules if rule.is_active),
        key=lambda rule: (
            rule.sequence,
            rule.code,
        ),
    )

    for rule in active_rules:

        if rule.calculation_type == CalculationType.FIXED:
            amount = Decimal(str(rule.amount or 0))
            rate = amount

        elif rule.calculation_type == CalculationType.PERCENTAGE:
            rate = Decimal(str(rule.percentage or 0))

            if rate < Decimal("0"):
                raise ValueError(f"Percentage cannot be negative: {rule.code}")

            amount = values["gross"] * rate / Decimal("100")

        elif rule.calculation_type == CalculationType.FORMULA:
            amount = _safe_formula(
                rule.formula or "",
                values,
            )
            rate = amount

        else:
            raise ValueError(f"Unsupported calculation type: {rule.code}")

        amount = money(amount)

        if amount < Decimal("0"):
            raise ValueError(f"Salary rule produced a negative amount: {rule.code}")

        if rule.category == SalaryRuleCategory.EARNING:
            values["total_earnings"] = money(values["total_earnings"] + amount)

            values["gross"] = money(values["total_earnings"])

        elif rule.category == SalaryRuleCategory.DEDUCTION:
            values["total_deductions"] = money(values["total_deductions"] + amount)

        elif rule.category == SalaryRuleCategory.TAX:
            values["total_tax"] = money(values["total_tax"] + amount)

        elif rule.category == SalaryRuleCategory.EMPLOYER_CONTRIBUTION:
            # Employer contributions are recorded as salary lines
            # but do not affect employee gross or net salary.
            pass

        else:
            raise ValueError(f"Unsupported salary rule category: {rule.code}")

        lines.append(
            {
                "salary_rule_id": rule.id,
                "rule_code": rule.code,
                "rule_name": rule.name,
                "category": rule.category.value,
                "quantity": Decimal("1"),
                "rate": rate,
                "amount": amount,
                "sequence": rule.sequence,
            }
        )

    values["gross"] = money(values["total_earnings"])

    values["net"] = money(
        values["gross"] - values["total_deductions"] - values["total_tax"]
    )

    if values["net"] < Decimal("0"):
        raise ValueError("Salary calculation produced a negative net salary")

    return {
        "gross": values["gross"],
        "deductions": money(values["total_deductions"]),
        "tax": money(values["total_tax"]),
        "net": values["net"],
        "lines": lines,
    }
