from django.shortcuts import render
from django.http import HttpResponse
from .sniffer import start_sniffing
from .system_monitor import get_system_stats
from .models import Packet, SystemStat, NetworkAnomaly
import threading
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.http import JsonResponse
from .system_monitor import get_system_stats
from django.db.models import Q
import logging


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
