from decimal import Decimal, ROUND_HALF_UP

MONEY_QUANTUM = Decimal("0.01")
HOURS_QUANTUM = Decimal("0.01")


def money(
    value: Decimal | int | str,
) -> Decimal:
    return Decimal(str(value)).quantize(
        MONEY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def calculate_worked_hours(
    check_in,
    check_out,
) -> Decimal:
    if check_in is None or check_out is None:
        return Decimal("0.00")

    if check_out < check_in:
        raise ValueError("check_out cannot be before check_in")

    seconds = Decimal(str((check_out - check_in).total_seconds()))

    hours = seconds / Decimal("3600")

    return hours.quantize(
        HOURS_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def calculate_overtime(
    worked: Decimal | int | str,
    expected: Decimal | int | str,
) -> Decimal:
    worked = Decimal(str(worked))
    expected = Decimal(str(expected))

    if worked < 0:
        raise ValueError("Worked hours cannot be negative")

    if expected < 0:
        raise ValueError("Expected hours cannot be negative")

    overtime = max(
        Decimal("0"),
        worked - expected,
    )

    return overtime.quantize(
        HOURS_QUANTUM,
        rounding=ROUND_HALF_UP,
    )
