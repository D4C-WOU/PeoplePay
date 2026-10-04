from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .dashboard import get_dashboard_data


class FilteredDashboardView(APIView):
    # Dashboard data is available to every authenticated workspace user.
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            get_dashboard_data(
                period_start=request.query_params.get("period_start"),
                period_end=request.query_params.get("period_end"),
                department_id=request.query_params.get("department"),
                employee_type=request.query_params.get("employee_type"),
            )
        )
