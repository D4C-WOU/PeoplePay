import ast
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from app.models.salary_rule import CalculationType, SalaryRule, SalaryRuleCategory
from app.utils.calculations import money

_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)
_ALLOWED_UNARY = (ast.UAdd, ast.USub)
_ALLOWED_NAMES = {
    "base_salary", "gross", "total_earnings", "total_deductions", "total_tax",
    "worked_days", "overtime_hours",
}


def _safe_formula(formula: str, variables: dict[str, Decimal]) -> Decimal:
    tree = ast.parse(formula, mode="eval")
    for node in ast.walk(tree):
        if isinstance(node, ast.Expression | ast.Constant):
            if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric constants are allowed")
        elif isinstance(node, ast.Name):
            if node.id not in _ALLOWED_NAMES:
                raise ValueError(f"Unsupported formula variable: {node.id}")
        elif isinstance(node, ast.BinOp):
            if not isinstance(node.op, _ALLOWED_BINOPS):
                raise ValueError("Unsupported formula operator")
        elif isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, _ALLOWED_UNARY):
                raise ValueError("Unsupported formula operator")
        elif isinstance(node, ast.Load):
            continue
        else:
            raise ValueError("Unsupported formula expression")
    compiled = compile(tree, "<salary_formula>", "eval")
    # Decimal arithmetic only; constants are converted to Decimal before use.
    safe_vars = {k: Decimal(str(v)) for k, v in variables.items()}
    return Decimal(str(eval(compiled, {"__builtins__": {}}, safe_vars)))


def calculate_salary(base_salary: Decimal, rules: list[SalaryRule], *,
                     worked_days: Decimal = Decimal("0"),
                     overtime_hours: Decimal = Decimal("0")) -> dict[str, Any]:
    values = {
        "base_salary": money(base_salary), "gross": money(base_salary),
        "total_earnings": money(base_salary), "total_deductions": Decimal("0"),
        "total_tax": Decimal("0"), "worked_days": worked_days,
        "overtime_hours": overtime_hours,
    }
    lines = []
    for rule in sorted((r for r in rules if r.is_active), key=lambda r: (r.sequence, r.code)):
        if rule.calculation_type == CalculationType.FIXED:
            amount = Decimal(rule.amount or 0)
            rate = amount
        elif rule.calculation_type == CalculationType.PERCENTAGE:
            rate = Decimal(rule.percentage or 0)
            amount = values["gross"] * rate / Decimal("100")
        else:
            amount = _safe_formula(rule.formula or "", values)
            rate = amount
        amount = money(amount)
        if rule.category == SalaryRuleCategory.EARNING:
            values["total_earnings"] += amount
            values["gross"] = money(values["total_earnings"])
        elif rule.category == SalaryRuleCategory.DEDUCTION:
            values["total_deductions"] += amount
        elif rule.category == SalaryRuleCategory.TAX:
            values["total_tax"] += amount
        # Employer contributions are intentionally excluded from employee net.
        lines.append({
            "salary_rule_id": rule.id, "rule_code": rule.code, "rule_name": rule.name,
            "category": rule.category.value, "quantity": Decimal("1"),
            "rate": rate, "amount": amount, "sequence": rule.sequence,
        })
    # Base salary is always the foundation of gross pay.
    values["gross"] = money(values["total_earnings"])
    values["net"] = money(values["gross"] - values["total_deductions"] - values["total_tax"])
    return {"gross": values["gross"], "deductions": money(values["total_deductions"]),
            "tax": money(values["total_tax"]), "net": values["net"], "lines": lines}
