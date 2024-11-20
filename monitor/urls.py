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
    path('network-analysis/', views.network_analysis_view, name='network_analysis'),
    path('alerts/', views.alert_dashboard, name='alert_dashboard'),
    path('alerts/thresholds/', views.manage_thresholds, name='manage_thresholds'),
    path('alerts/acknowledge/<int:alert_id>/', views.acknowledge_alert, name='acknowledge_alert'),
    path('alerts/resolve/<int:alert_id>/', views.resolve_alert, name='resolve_alert'),
    path('alerts/test/', views.test_alert, name='test_alert'),
]
