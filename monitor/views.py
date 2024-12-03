import csv
import json
import logging
import threading
from datetime import timedelta
import os

from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import psutil

from .alert_service import check_threshold
from .forms import AlertThresholdForm
from .models import Alert, AlertThreshold, NetworkAnomaly, Packet, SystemStat
from .sniffer import start_sniffing
from .system_monitor import get_system_stats

logger = logging.getLogger(__name__)


def dashboard_view(request):
    """Main dashboard view showing system overview."""
    recent_packets = Packet.objects.all().order_by("-timestamp")[:10]

    # Format the packets for better display
    formatted_packets = []
    for packet in recent_packets:
        formatted_packets.append(
            {
                "timestamp": packet.timestamp,
                "protocol": packet.protocol,
                "source": f"{packet.source_ip}:{packet.source_port}"
                if packet.source_port
                else packet.source_ip,
                "destination": f"{packet.destination_ip}:{packet.destination_port}"
                if packet.destination_port
                else packet.destination_ip,
                "size": packet.packet_size,
                "summary": str(packet),
            }
        )

    context = {
        "recent_packets": formatted_packets,
        "packet_count": Packet.objects.count(),
        "latest_stats": SystemStat.objects.last(),
    }
    return render(request, "monitor/dashboard.html", context)


sniffing_thread = None
sniffing_active = False
capture_manager = None


def start_sniffing_view(request):
    global sniffing_thread, sniffing_active, capture_manager

    if request.method == "POST":
        action = request.POST.get("action")

        try:
            if action == "start" and not sniffing_active:
                sniffing_active = True
                capture_manager = start_sniffing()
                if capture_manager:
                    logger.info("Packet capture started successfully")
                    return JsonResponse({"status": "success", "message": "Packet sniffing started!"})
                else:
                    sniffing_active = False
                    return JsonResponse(
                        {"status": "error", "message": "Failed to start packet capture"},
                        status=500
                    )

            elif action == "stop" and sniffing_active:
                if capture_manager:
                    capture_manager.stop_capture()
                sniffing_active = False
                logger.info("Packet capture stopped")
                return JsonResponse({"status": "success", "message": "Packet sniffing stopped!"})

        except Exception as e:
            logger.error(f"Error in packet capture: {e}", exc_info=True)
            sniffing_active = False
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=500
            )

    # Get interface list for the template
    available_interfaces = []
    try:
        if os.name == 'nt':  # Windows
            from scapy.arch.windows import get_windows_if_list
            interfaces = get_windows_if_list()
            available_interfaces = [iface['name'] for iface in interfaces if iface['name']]
        else:
            available_interfaces = [
                iface
                for iface, addrs in psutil.net_if_addrs().items()
                if any(addr.family == 2 for addr in addrs)
            ]
    except Exception as e:
        logger.error(f"Error getting interfaces: {e}")
        available_interfaces = ["Wi-Fi"]

    return render(request, "monitor/start_sniffing.html", {
        "sniffing_active": sniffing_active,
        "available_interfaces": available_interfaces
    })


def system_stats_view(request):
    try:
        stats = get_system_stats()
        logger.debug(f"Retrieved stats: {stats}")  # Log the stats
        return render(request, "monitor/system_stats.html", {"stats": stats})
    except Exception as e:
        logger.error(f"Error in system_stats_view: {str(e)}", exc_info=True)
        return HttpResponse(f"An error occurred: {str(e)}", status=500)


def packet_history_view(request):
    try:
        packets = Packet.objects.order_by("-timestamp")[:1000]  # Limit to last 1000
        return render(request, "monitor/packet_history.html", {"packets": packets})
    except Exception as e:
        logger.error(f"Error in packet_history_view: {str(e)}", exc_info=True)
        return HttpResponse(f"Error: {str(e)}", status=500)


def system_stats_history_view(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    stats = SystemStat.objects.all().order_by("timestamp")

    if start_date and end_date:
        stats = stats.filter(timestamp__range=[start_date, end_date])

    # Prepare data for charts
    chart_data = {
        "labels": [stat.timestamp.strftime("%Y-%m-%d %H:%M:%S") for stat in stats],
        "cpu_data": [stat.cpu_usage for stat in stats],
        "memory_data": [stat.memory_usage for stat in stats],
        "disk_data": [stat.disk_usage for stat in stats],
        "network_sent": [stat.bytes_sent for stat in stats],
        "network_recv": [stat.bytes_recv for stat in stats],
    }

    # Convert to JSON for JavaScript
    chart_data_json = json.dumps(chart_data, cls=DjangoJSONEncoder)

    return render(
        request,
        "monitor/system_stats_history.html",
        {
            "stats": stats,
            "chart_data_json": chart_data_json,
        },
    )


def system_stats_json(request):
    stats = get_system_stats()
    return JsonResponse(stats)


def anomalies_view(request):
    recent_anomalies = NetworkAnomaly.objects.filter(resolved=False).order_by(
        "-timestamp"
    )[:10]
    return render(
        request, "monitor/anomalies.html", {"recent_anomalies": recent_anomalies}
    )


def get_protocol_distribution():
    return (
        Packet.objects.values("protocol").annotate(count=Count("id")).order_by("-count")
    )


def get_top_talkers():
    return (
        Packet.objects.values("source_ip")
        .annotate(packet_count=Count("id"), total_bytes=Sum("packet_size"))
        .order_by("-packet_count")[:10]
    )


def get_port_activity():
    return (
        Packet.objects.filter(destination_port__isnull=False)
        .values("destination_port")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )


def network_analysis_view(request):
    # Get protocol distribution
    protocol_dist = list(
        Packet.objects.values("protocol").annotate(count=Count("id")).order_by("-count")
    )
    print("Protocol Distribution:", protocol_dist)  # Debug print

    # Get top talkers
    top_talkers = list(
        Packet.objects.values("source_ip")
        .annotate(packet_count=Count("id"), total_bytes=Sum("packet_size"))
        .exclude(source_ip__isnull=True)
        .order_by("-packet_count")[:10]
    )
    print("Top Talkers:", top_talkers)  # Debug print

    # Get port activity
    port_activity = list(
        Packet.objects.values("destination_port")
        .annotate(count=Count("id"))
        .exclude(destination_port__isnull=True)
        .order_by("-count")[:10]
    )
    print("Port Activity:", port_activity)  # Debug print

    # Create context with debug information
    context = {
        "protocol_distribution": json.dumps(protocol_dist, cls=DjangoJSONEncoder),
        "top_talkers": json.dumps(top_talkers, cls=DjangoJSONEncoder),
        "port_activity": json.dumps(port_activity, cls=DjangoJSONEncoder),
        "debug_packet_count": Packet.objects.count(),  # Add total packet count
    }

    print("Context being sent to template:", context)  # Debug print
    return render(request, "monitor/network_analysis.html", context)


def alert_dashboard(request):
    active_alerts = Alert.objects.filter(resolved=False)
    resolved_alerts = Alert.objects.filter(resolved=True)
    thresholds = AlertThreshold.objects.all()

    context = {
        "active_alerts": active_alerts,
        "resolved_alerts": resolved_alerts,
        "thresholds": thresholds,
    }
    return render(request, "monitor/alert_dashboard.html", context)


def manage_thresholds(request):
    if request.method == "POST":
        form = AlertThresholdForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Alert threshold created successfully.")
            return redirect("alert_dashboard")
    else:
        form = AlertThresholdForm()

    thresholds = AlertThreshold.objects.all()
    return render(
        request,
        "monitor/manage_thresholds.html",
        {"form": form, "thresholds": thresholds},
    )


def acknowledge_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    if request.method == "POST":
        alert.acknowledged = True
        alert.acknowledged_by = request.user.username
        alert.acknowledged_at = timezone.now()
        alert.notes = request.POST.get("notes", "")
        alert.save()
        messages.success(request, "Alert acknowledged successfully.")
    return redirect("alert_dashboard")


def resolve_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    if request.method == "POST":
        alert.resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        messages.success(request, "Alert resolved successfully.")
    return redirect("alert_dashboard")


def test_alert(request):
    """Test function to trigger an alert"""
    # Create a test threshold if it doesn't exist
    threshold, created = AlertThreshold.objects.get_or_create(
        name="High CPU Usage Test",
        defaults={
            "metric": "cpu_usage",
            "threshold_value": 80.0,
            "severity": "high",
            "enabled": True,
            "email_notification": True,
            "notification_email": "test@example.com",
            "description": "Test alert for CPU usage above 80%",
        },
    )

    # Simulate a high CPU value
    check_threshold("cpu_usage", 85.0)

    messages.success(
        request,
        "Test alert has been triggered. Check the console for the email output.",
    )
    return redirect("alert_dashboard")


def export_packets_csv(request):
    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="packet_history_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "Timestamp",
            "Protocol",
            "Source IP",
            "Source Port",
            "Destination IP",
            "Destination Port",
            "Size",
            "Summary",
        ]
    )

    packets = Packet.objects.all().order_by("-timestamp")
    for packet in packets:
        writer.writerow(
            [
                packet.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                packet.protocol,
                packet.source_ip,
                packet.source_port,
                packet.destination_ip,
                packet.destination_port,
                packet.packet_size,
                str(packet),
            ]
        )

    return response


def export_packets_json(request):
    packets = Packet.objects.all().order_by("-timestamp")
    packet_list = []

    for packet in packets:
        packet_list.append(
            {
                "timestamp": packet.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "protocol": packet.protocol,
                "source_ip": packet.source_ip,
                "source_port": packet.source_port,
                "destination_ip": packet.destination_ip,
                "destination_port": packet.destination_port,
                "size": packet.packet_size,
                "summary": str(packet),
            }
        )

    response = HttpResponse(
        json.dumps(packet_list, indent=2), content_type="application/json"
    )
    response[
        "Content-Disposition"
    ] = f'attachment; filename="packet_history_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response
