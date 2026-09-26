from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin panel
    path("admin/", admin.site.urls),
    # REST API
    path("api/", include("api.urls")),
]
