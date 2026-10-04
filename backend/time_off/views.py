from datetime import date

from django.core.exceptions import ValidationError

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsHRManager
from time_off.models import TimeOffAllocation, TimeOffRequest, TimeOffType
from time_off.services import (
    approve_time_off_allocation,
    reject_time_off_allocation,
    approve_time_off_request,
)


class ApproveTimeOffAllocationView(APIView):
    # Allocation approval is an HR operation.
    permission_classes = [IsAuthenticated, IsHRManager]

    def post(self, request, pk):
        allocation = TimeOffAllocation.objects.get(pk=pk)
        try:
            allocation = approve_time_off_allocation(allocation, request.user)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=400)

        return Response({"id": allocation.id, "status": allocation.status})


class RejectTimeOffAllocationView(APIView):
    # Allocation rejection is also restricted to HR roles.
    permission_classes = [IsAuthenticated, IsHRManager]

    def post(self, request, pk):
        allocation = TimeOffAllocation.objects.get(pk=pk)
        try:
            allocation = reject_time_off_allocation(allocation, request.user)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=400)

        return Response({"id": allocation.id, "status": allocation.status})


class CreateTimeOffAllocationView(APIView):
    permission_classes = [IsAuthenticated, IsHRManager]

    def post(self, request):
        allocation_year = int(request.data.get("allocation_year"))
        allocated_days = request.data.get("allocated_days")
        allocation = TimeOffAllocation.objects.create(
            employee_id=request.data.get("employee"),
            time_off_type_id=request.data.get("time_off_type"),
            allocation_year=allocation_year,
            allocated_days=allocated_days,
            valid_from=request.data.get("valid_from") or f"{allocation_year}-01-01",
            valid_until=request.data.get("valid_until") or f"{allocation_year}-12-31",
        )
        return Response({"id": allocation.id, "status": allocation.status}, status=201)


class CreateTimeOffRequestView(APIView):
    permission_classes = [IsAuthenticated, IsHRManager]

    def post(self, request):
        start_date = date.fromisoformat(request.data["start_date"])
        end_date = date.fromisoformat(request.data["end_date"])
        if end_date < start_date:
            return Response(
                {"detail": "End date cannot be before start date."}, status=400
            )

        time_off_type = TimeOffType.objects.get(pk=request.data.get("time_off_type"))
        request_obj = TimeOffRequest.objects.create(
            employee_id=request.data.get("employee"),
            time_off_type=time_off_type,
            start_date=start_date,
            end_date=end_date,
            requested_days=(end_date - start_date).days + 1,
            reason=request.data.get("reason", ""),
        )

        if not time_off_type.requires_approval:
            try:
                approve_time_off_request(request_obj, request.user)
            except ValidationError as exc:
                request_obj.delete()
                return Response({"detail": str(exc)}, status=400)

        return Response(
            {"id": request_obj.id, "status": request_obj.status}, status=201
        )
