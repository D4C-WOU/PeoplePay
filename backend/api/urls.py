from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import CurrentUserView

urlpatterns = [
    # Login and receive access + refresh tokens
    path(
        "auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    # Get a new access token using a refresh token
    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    # Get information about the currently authenticated user
    path(
        "auth/me/",
        CurrentUserView.as_view(),
        name="current_user",
    ),
]
