from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CurrentUserSerializer


class CurrentUserView(APIView):
    # Require a valid JWT before returning user information
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Serialize the authenticated user
        serializer = CurrentUserSerializer(request.user)

        # Return the current user's account information
        return Response(serializer.data)
