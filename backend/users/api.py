from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsAdmin

User = get_user_model()


def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_active": user.is_active,
    }


class UserListView(APIView):
    # Only Admin can manage workspace accounts.
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all().order_by("username")
        return Response([serialize_user(user) for user in users])


class UserUpdateView(APIView):
    # Only Admin can change another user's access.
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        user = User.objects.get(pk=pk)

        if "role" in request.data:
            valid_roles = {choice[0] for choice in User.Role.choices}
            if request.data["role"] not in valid_roles:
                return Response({"detail": "Invalid user role."}, status=400)
            user.role = request.data["role"]

        if "is_active" in request.data:
            user.is_active = bool(request.data["is_active"])

        user.save(update_fields=["role", "is_active"])
        return Response(serialize_user(user))
