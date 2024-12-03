from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("monitor/", include("monitor.urls")),  # Remove namespace parameter
]
