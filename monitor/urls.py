from django.urls import path

from . import views

app_name = "monitor"

urlpatterns = [
    # Dashboard
    path("", views.dashboard_view, name="dashboard"),
    # System Stats
    path("system-stats/", views.system_stats_view, name="system_stats"),
    path("system-stats-json/", views.system_stats_json, name="system_stats_json"),
    path(
        "system-stats-history/",
        views.system_stats_history_view,
        name="system_stats_history",
    ),
    # Packet Capture
    path("start-sniffing/", views.start_sniffing_view, name="start_sniffing"),
    path("packet-history/", views.packet_history_view, name="packet_history"),
    path(
        "packet-history/export/csv/",
        views.export_packets_csv,
        name="export_packets_csv",
    ),
    path(
        "packet-history/export/json/",
        views.export_packets_json,
        name="export_packets_json",
    ),
    # Analysis
    path("network-analysis/", views.network_analysis_view, name="network_analysis"),
    path("anomalies/", views.anomalies_view, name="anomalies"),
    # Alerts
    path("alerts/", views.alert_dashboard, name="alert_dashboard"),
    path("alerts/thresholds/", views.manage_thresholds, name="manage_thresholds"),
    path(
        "alerts/acknowledge/<int:alert_id>/",
        views.acknowledge_alert,
        name="acknowledge_alert",
    ),
    path("alerts/resolve/<int:alert_id>/", views.resolve_alert, name="resolve_alert"),
    path("alerts/test/", views.test_alert, name="test_alert"),
]
