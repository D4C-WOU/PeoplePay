from decimal import Decimal, ROUND_HALF_UP

MONEY_QUANTUM = Decimal("0.01")


def money(value: Decimal | int | str) -> Decimal:
    return Decimal(value).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def calculate_worked_hours(check_in, check_out) -> Decimal:
    if not check_in or not check_out:
        return Decimal("0")
    seconds = Decimal(str((check_out - check_in).total_seconds()))
    return (seconds / Decimal("3600")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_overtime(worked: Decimal, expected: Decimal) -> Decimal:
    return max(Decimal("0"), worked - expected).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
