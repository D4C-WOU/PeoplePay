from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# Admin configuration for the HR system
@admin.register(User)
class UserAdmin(UserAdmin):

    # columns displayed to admin when viewing list of users
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
    )

    # filters to make it easier for the admin to find users
    list_filter = (
        "role",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    # controls how existing user is displayed
    fieldsets = UserAdmin.fieldsets + (
        (
            "PeoplePay360 Role",
            {
                "fields": ("role",),
            },
        ),
    )

    # controls the form used when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "PeoplePay360 Role",
            {
                "fields": ("role",),
            },
        ),
    )
