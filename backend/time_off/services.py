from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import TimeOffAllocation, TimeOffRequest


def get_available_allocation(employee, time_off_type, request_date: date):
    # Find approved allocations valid for the requested date
    allocations = TimeOffAllocation.objects.filter(
        employee=employee,
        time_off_type=time_off_type,
        status=TimeOffAllocation.Status.APPROVED,
        valid_from__lte=request_date,
        valid_until__gte=request_date,
    ).order_by("-allocation_year")

    # Return the first allocation with remaining balance
    for allocation in allocations:
        if allocation.remaining_days > 0:
            return allocation

    # No usable allocation was found
    return None


@transaction.atomic  # treats whole operation as 1 db transaction
def approve_time_off_request(request, reviewer):
    # Prevent an already processed request from being approved again
    if request.status != TimeOffRequest.Status.PENDING:
        raise ValidationError("Only pending time-off requests can be approved.")

    # Find an approved allocation when the type requires one
    allocation = None

    if request.time_off_type.requires_allocation:
        allocation = get_available_allocation(
            request.employee,
            request.time_off_type,
            request.start_date,
        )

        # Approval cannot continue without enough available leave
        if allocation is None:
            raise ValidationError("No approved time-off allocation is available.")

        # Make sure the allocation can cover the complete request
        if allocation.remaining_days < request.requested_days:
            raise ValidationError(
                "Time-off allocation does not have enough remaining days."
            )

    # Mark the request as approved
    request.status = TimeOffRequest.Status.APPROVED
    request.reviewed_by = reviewer
    request.reviewed_at = timezone.now()
    request.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
        ]
    )

    # Deduct the approved days from the allocation
    if allocation is not None:
        allocation.used_days += request.requested_days
        allocation.save(update_fields=["used_days"])

    # Return both objects for further use
    return request, allocation


@transaction.atomic
def reject_time_off_request(request, reviewer):
    # Prevent an already processed request from being rejected again
    if request.status != TimeOffRequest.Status.PENDING:
        raise ValidationError("Only pending time-off requests can be rejected.")

    # Mark the request as rejected
    request.status = TimeOffRequest.Status.REJECTED
    request.reviewed_by = reviewer
    request.reviewed_at = timezone.now()
    request.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
        ]
    )

    # Rejected requests do not change any allocation
    return request
