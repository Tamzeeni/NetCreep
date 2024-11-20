from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("system-stats/", views.system_stats_view, name="system_stats"),
    path("start-sniffing/", views.start_sniffing_view, name="start_sniffing"),
    path("packet-history/", views.packet_history_view, name="packet_history"),
    path(
        "system-stats-history/",
        views.system_stats_history_view,
        name="system_stats_history",
    ),
    path("system-stats-json/", views.system_stats_json, name="system_stats_json"),
    path("anomalies/", views.anomalies_view, name="anomalies"),
]
