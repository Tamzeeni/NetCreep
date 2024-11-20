from django.shortcuts import render
from django.http import HttpResponse
from .sniffer import start_sniffing
from .system_monitor import get_system_stats
from .models import Packet, SystemStat, NetworkAnomaly
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import AlertThreshold, Alert
from .forms import AlertThresholdForm
import threading
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.http import JsonResponse
from .system_monitor import get_system_stats
from django.db.models import Q
import logging
from .alert_service import check_threshold
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta


logger = logging.getLogger(__name__)

def dashboard_view(request):
    # Get initial data for first page load
    initial_stats = get_system_stats()
    return render(request, 'monitor/dashboard.html', {
        'initial_stats': initial_stats
    })


sniffing_thread = None
sniffing_active = False


def start_sniffing_view(request):
    global sniffing_thread, sniffing_active

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "start" and not sniffing_active:
            sniffing_active = True
            sniffing_thread = threading.Thread(target=start_sniffing)
            sniffing_thread.start()
            return HttpResponse("Packet sniffing started!")

        elif action == "stop" and sniffing_active:
            sniffing_active = False
            if sniffing_thread:
                sniffing_thread.join()  # Wait for the thread to finish
            return HttpResponse("Packet sniffing stopped!")

    return render(request, "monitor/start_sniffing.html")


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
        packets = Packet.objects.order_by('-timestamp')[:1000]  # Limit to last 1000
        return render(request, 'monitor/packet_history.html', {'packets': packets})
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
    return (Packet.objects
            .values('protocol')
            .annotate(count=Count('id'))
            .order_by('-count'))

def get_top_talkers():
    return (Packet.objects
            .values('src_ip')
            .annotate(
                packet_count=Count('id'),
                total_bytes=Sum('size')
            )
            .order_by('-packet_count')[:10])

def get_port_activity():
    return (Packet.objects
            .filter(dst_port__isnull=False)
            .values('dst_port')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])

def network_analysis_view(request):
    # Get protocol distribution
    protocol_dist = list(Packet.objects
        .values('protocol')
        .annotate(count=Count('id'))
        .order_by('-count'))
    print("Protocol Distribution:", protocol_dist)  # Debug print

    # Get top talkers
    top_talkers = list(Packet.objects
        .values('src_ip')
        .annotate(
            packet_count=Count('id'),
            total_bytes=Sum('size')
        )
        .exclude(src_ip__isnull=True)
        .order_by('-packet_count')[:10])
    print("Top Talkers:", top_talkers)  # Debug print

    # Get port activity
    port_activity = list(Packet.objects
        .values('dst_port')
        .annotate(count=Count('id'))
        .exclude(dst_port__isnull=True)
        .order_by('-count')[:10])
    print("Port Activity:", port_activity)  # Debug print

    # Create context with debug information
    context = {
        'protocol_distribution': json.dumps(protocol_dist, cls=DjangoJSONEncoder),
        'top_talkers': json.dumps(top_talkers, cls=DjangoJSONEncoder),
        'port_activity': json.dumps(port_activity, cls=DjangoJSONEncoder),
        'debug_packet_count': Packet.objects.count()  # Add total packet count
    }

    print("Context being sent to template:", context)  # Debug print
    return render(request, 'monitor/network_analysis.html', context)



def alert_dashboard(request):
    active_alerts = Alert.objects.filter(resolved=False)
    resolved_alerts = Alert.objects.filter(resolved=True)
    thresholds = AlertThreshold.objects.all()
    
    context = {
        'active_alerts': active_alerts,
        'resolved_alerts': resolved_alerts,
        'thresholds': thresholds,
    }
    return render(request, 'monitor/alert_dashboard.html', context)

def manage_thresholds(request):
    if request.method == 'POST':
        form = AlertThresholdForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alert threshold created successfully.')
            return redirect('alert_dashboard')
    else:
        form = AlertThresholdForm()
    
    thresholds = AlertThreshold.objects.all()
    return render(request, 'monitor/manage_thresholds.html', {
        'form': form,
        'thresholds': thresholds
    })

def acknowledge_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    if request.method == 'POST':
        alert.acknowledged = True
        alert.acknowledged_by = request.user.username
        alert.acknowledged_at = timezone.now()
        alert.notes = request.POST.get('notes', '')
        alert.save()
        messages.success(request, 'Alert acknowledged successfully.')
    return redirect('alert_dashboard')

def resolve_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    if request.method == 'POST':
        alert.resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        messages.success(request, 'Alert resolved successfully.')
    return redirect('alert_dashboard')

def test_alert(request):
    """Test function to trigger an alert"""
    # Create a test threshold if it doesn't exist
    threshold, created = AlertThreshold.objects.get_or_create(
        name="High CPU Usage Test",
        defaults={
            'metric': 'cpu_usage',
            'threshold_value': 80.0,
            'severity': 'high',
            'enabled': True,
            'email_notification': True,
            'notification_email': 'test@example.com',
            'description': 'Test alert for CPU usage above 80%'
        }
    )
    
    # Simulate a high CPU value
    check_threshold('cpu_usage', 85.0)
    
    messages.success(request, 'Test alert has been triggered. Check the console for the email output.')
    return redirect('alert_dashboard')