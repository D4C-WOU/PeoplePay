from rest_framework import serializers

from users.models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    # Return the user's basic account information
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = fields
