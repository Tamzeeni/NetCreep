import time

import psutil

from .models import SystemStat
from .utils import broadcast_update


def get_system_stats():
    # Get CPU usage with a shorter interval
    cpu_usage = psutil.cpu_percent(interval=0.1)

    # Get memory information
    memory = psutil.virtual_memory()

    # Get disk information
    disk = psutil.disk_usage("/")

    # Get network information
    network = psutil.net_io_counters()

    stats = {
        "cpu_usage": cpu_usage,
        "memory_usage": memory.percent,
        "disk_usage": disk.percent,
        "network_io": {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
        },
        "timestamp": time.time(),
    }

    # Save to database (but not too frequently)
    try:
        latest_stat = SystemStat.objects.latest("timestamp")
        time_diff = time.time() - latest_stat.timestamp.timestamp()
        if time_diff > 60:  # Save only every minute
            SystemStat.objects.create(
                cpu_usage=stats["cpu_usage"],
                memory_usage=stats["memory_usage"],
                disk_usage=stats["disk_usage"],
                bytes_sent=stats["network_io"]["bytes_sent"],
                bytes_recv=stats["network_io"]["bytes_recv"],
            )
    except SystemStat.DoesNotExist:
        # If no previous stat exists, create one
        SystemStat.objects.create(
            cpu_usage=stats["cpu_usage"],
            memory_usage=stats["memory_usage"],
            disk_usage=stats["disk_usage"],
            bytes_sent=stats["network_io"]["bytes_sent"],
            bytes_recv=stats["network_io"]["bytes_recv"],
        )

    return stats
