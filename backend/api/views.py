from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import (
    IsAdmin,
    IsHRManager,
    IsHRPayrollManager,
    IsHRPayrollUser,
)
from .serializers import CurrentUserSerializer


class CurrentUserView(APIView):
    # Require a valid JWT before returning user information
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Serialize the authenticated user
        serializer = CurrentUserSerializer(request.user)

        # Return the current user's account information
        return Response(serializer.data)


class HRManagerTestView(APIView):
    # Require HR Manager access or higher
    permission_classes = [IsHRManager]

    def get(self, request):
        # Confirm that the current user passed the permission check
        return Response(
            {
                "message": "HR Manager access granted.",
                "role": request.user.role,
            }
        )


class HRPayrollUserTestView(APIView):
    # Require Payroll User access or higher
    permission_classes = [IsHRPayrollUser]

    def get(self, request):
        # Confirm that the current user passed the permission check
        return Response(
            {
                "message": "HR Payroll User access granted.",
                "role": request.user.role,
            }
        )


class HRPayrollManagerTestView(APIView):
    # Require Payroll Manager access or higher
    permission_classes = [IsHRPayrollManager]

    def get(self, request):
        # Confirm that the current user passed the permission check
        return Response(
            {
                "message": "HR Payroll Manager access granted.",
                "role": request.user.role,
            }
        )


class AdminTestView(APIView):
    # Require Admin access
    permission_classes = [IsAdmin]

    def get(self, request):
        # Confirm that the current user passed the permission check
        return Response(
            {
                "message": "Admin access granted.",
                "role": request.user.role,
            }
        )
