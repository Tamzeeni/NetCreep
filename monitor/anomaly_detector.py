from collections import deque
import numpy as np
from .models import NetworkAnomaly, SystemStat
from django.db.models import Avg, StdDev
from django.utils import timezone
from datetime import timedelta


class AnomalyDetector:
    def __init__(self):
        self.window_size = 60  # 1 hour (assuming measurements every minute)
        self.traffic_history = deque(maxlen=self.window_size)
        self.threshold_multiplier = 2.0

    def calculate_baseline_stats(self):
        # Get stats from the last 24 hours
        last_24h = timezone.now() - timedelta(hours=24)
        stats = SystemStat.objects.filter(timestamp__gte=last_24h)

        return {
            "cpu_mean": stats.aggregate(Avg("cpu_usage"))["cpu_usage__avg"] or 0,
            "cpu_std": stats.aggregate(StdDev("cpu_usage"))["cpu_usage__stddev"] or 0,
            "memory_mean": stats.aggregate(Avg("memory_usage"))["memory_usage__avg"]
            or 0,
            "memory_std": stats.aggregate(StdDev("memory_usage"))[
                "memory_usage__stddev"
            ]
            or 0,
            "network_mean": stats.aggregate(Avg("bytes_sent"))["bytes_sent__avg"] or 0,
            "network_std": stats.aggregate(StdDev("bytes_sent"))["bytes_sent__stddev"]
            or 0,
        }

    def detect_anomalies(self, current_stats):
        baseline = self.calculate_baseline_stats()
        anomalies = []

        # CPU Usage Anomaly
        if current_stats["cpu_usage"] > baseline["cpu_mean"] + (
            self.threshold_multiplier * baseline["cpu_std"]
        ):
            anomalies.append(
                {
                    "type": "CPU_SPIKE",
                    "description": f"Unusual CPU usage detected: {current_stats['cpu_usage']}%",
                    "severity": "HIGH" if current_stats["cpu_usage"] > 90 else "MEDIUM",
                }
            )

        # Memory Usage Anomaly
        if current_stats["memory_usage"] > baseline["memory_mean"] + (
            self.threshold_multiplier * baseline["memory_std"]
        ):
            anomalies.append(
                {
                    "type": "MEMORY_SPIKE",
                    "description": f"Unusual memory usage detected: {current_stats['memory_usage']}%",
                    "severity": (
                        "HIGH" if current_stats["memory_usage"] > 90 else "MEDIUM"
                    ),
                }
            )

        # Network Traffic Anomaly
        current_traffic = (
            current_stats["network_io"].bytes_sent
            + current_stats["network_io"].bytes_recv
        )
        if current_traffic > baseline["network_mean"] + (
            self.threshold_multiplier * baseline["network_std"]
        ):
            anomalies.append(
                {
                    "type": "NETWORK_SPIKE",
                    "description": f"Unusual network traffic detected: {current_traffic} bytes",
                    "severity": "HIGH",
                }
            )

        # Store detected anomalies
        for anomaly in anomalies:
            NetworkAnomaly.objects.create(**anomaly)

        return anomalies
