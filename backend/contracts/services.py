from datetime import date

from django.core.exceptions import ValidationError

from .models import Contract


def get_applicable_contract(employee, period_start: date, period_end: date):
    # Make sure the payroll period is valid
    if period_end < period_start:
        raise ValidationError("Payroll period end date cannot be before start date.")

    # Find contracts that started before the payroll period
    contracts = Contract.objects.filter(
        employee=employee,
        start_date__lte=period_start,
    ).order_by("-start_date")

    applicable_contract = None

    # Check which contract covers the complete payroll period
    for contract in contracts:
        # Open-ended contracts have no end date
        covers_period_end = contract.end_date is None or contract.end_date >= period_end

        if covers_period_end:
            # Prevent payroll from silently choosing between two contracts
            if applicable_contract is not None:
                raise ValidationError(
                    f"Multiple contracts apply to employee "
                    f"{employee.employee_number} for the selected payroll period."
                )

            applicable_contract = contract

    # Payroll cannot continue without an applicable contract
    if applicable_contract is None:
        raise ValidationError(
            f"No applicable contract found for employee "
            f"{employee.employee_number} for the selected payroll period."
        )

    # Return the contract payroll should use
    return applicable_contract
