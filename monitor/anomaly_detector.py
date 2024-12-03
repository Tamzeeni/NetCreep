import logging
from typing import Any, Dict, List

import numpy as np
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from scipy import stats

from .models import NetworkAnomaly, Packet, SystemStat

logger = logging.getLogger(__name__)


class AdvancedAnomalyDetector:
    """
    Advanced anomaly detection with multiple detection strategies
    """

    @classmethod
    def detect_network_anomalies(
        cls, time_window_hours: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Comprehensive network anomaly detection

        Args:
            time_window_hours (int): Hours to analyze for anomalies

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Protocol Distribution Anomalies
        protocol_anomalies = cls._detect_protocol_distribution_anomalies(
            time_window_hours
        )
        anomalies.extend(protocol_anomalies)

        # Traffic Volume Anomalies
        traffic_anomalies = cls._detect_traffic_volume_anomalies(time_window_hours)
        anomalies.extend(traffic_anomalies)

        # IP Address Behavior Anomalies
        ip_anomalies = cls._detect_ip_behavior_anomalies(time_window_hours)
        anomalies.extend(ip_anomalies)

        # Port Scan Detection
        port_scan_anomalies = cls._detect_port_scans(time_window_hours)
        anomalies.extend(port_scan_anomalies)

        return anomalies

    @classmethod
    def _detect_protocol_distribution_anomalies(
        cls, time_window_hours: int
    ) -> List[Dict[str, Any]]:
        """
        Detect unusual protocol distribution

        Args:
            time_window_hours (int): Hours to analyze

        Returns:
            List of protocol distribution anomalies
        """
        cutoff_time = timezone.now() - timezone.timedelta(hours=time_window_hours)
        protocol_counts = (
            Packet.objects.filter(timestamp__gte=cutoff_time)
            .values("protocol")
            .annotate(count=Count("id"))
        )

        total_packets = sum(proto["count"] for proto in protocol_counts)
        anomalies = []

        for proto in protocol_counts:
            percentage = (proto["count"] / total_packets) * 100

            # Unusual protocol percentage thresholds
            if proto["protocol"] == "TCP" and percentage > 90:
                anomalies.append(
                    {
                        "type": "Protocol Distribution",
                        "description": f"Unusually high TCP traffic: {percentage:.2f}%",
                        "severity": "MEDIUM",
                    }
                )

            if proto["protocol"] == "UDP" and percentage > 50:
                anomalies.append(
                    {
                        "type": "Protocol Distribution",
                        "description": f"Unusually high UDP traffic: {percentage:.2f}%",
                        "severity": "LOW",
                    }
                )

        return anomalies

    @classmethod
    def _detect_traffic_volume_anomalies(
        cls, time_window_hours: int
    ) -> List[Dict[str, Any]]:
        """
        Detect traffic volume anomalies using statistical methods

        Args:
            time_window_hours (int): Hours to analyze

        Returns:
            List of traffic volume anomalies
        """
        cutoff_time = timezone.now() - timezone.timedelta(hours=time_window_hours)
        packets = Packet.objects.filter(timestamp__gte=cutoff_time)

        # Packet size analysis
        sizes = [packet.size for packet in packets]

        if len(sizes) > 10:  # Ensure enough data points
            z_scores = np.abs(stats.zscore(sizes))
            outliers = np.where(z_scores > 3)[0]

            if len(outliers) > 0:
                return [
                    {
                        "type": "Traffic Volume",
                        "description": f"Detected {len(outliers)} unusual packet sizes",
                        "severity": "HIGH",
                    }
                ]

        return []

    @classmethod
    def _detect_ip_behavior_anomalies(
        cls, time_window_hours: int
    ) -> List[Dict[str, Any]]:
        """
        Detect unusual IP address behavior

        Args:
            time_window_hours (int): Hours to analyze

        Returns:
            List of IP behavior anomalies
        """
        cutoff_time = timezone.now() - timezone.timedelta(hours=time_window_hours)
        ip_stats = (
            Packet.objects.filter(timestamp__gte=cutoff_time)
            .values("src_ip")
            .annotate(packet_count=Count("id"), total_bytes=Sum("size"))
        )

        anomalies = []
        for ip_stat in ip_stats:
            # High packet count anomaly
            if ip_stat["packet_count"] > 1000:
                anomalies.append(
                    {
                        "type": "IP Behavior",
                        "description": f"High packet count from {ip_stat['src_ip']}: {ip_stat['packet_count']} packets",
                        "severity": "HIGH",
                    }
                )

            # Large data transfer anomaly
            if ip_stat["total_bytes"] > 100 * 1024 * 1024:  # 100 MB
                anomalies.append(
                    {
                        "type": "IP Behavior",
                        "description": f"Large data transfer from {ip_stat['src_ip']}: {ip_stat['total_bytes']} bytes",
                        "severity": "MEDIUM",
                    }
                )

        return anomalies

    @classmethod
    def _detect_port_scans(cls, time_window_hours: int) -> List[Dict[str, Any]]:
        """
        Detect potential port scanning activities

        Args:
            time_window_hours (int): Hours to analyze

        Returns:
            List of port scan anomalies
        """
        cutoff_time = timezone.now() - timezone.timedelta(hours=time_window_hours)
        port_stats = (
            Packet.objects.filter(timestamp__gte=cutoff_time, dst_port__isnull=False)
            .values("src_ip", "dst_port")
            .annotate(connection_count=Count("id"))
        )

        anomalies = []
        for stat in port_stats:
            # Potential port scan: many connections to different ports from same IP
            if stat["connection_count"] > 50:
                anomalies.append(
                    {
                        "type": "Port Scan",
                        "description": f"Potential port scan from {stat['src_ip']} to port {stat['dst_port']}",
                        "severity": "HIGH",
                    }
                )

        return anomalies

    @classmethod
    def save_anomalies(cls, anomalies: List[Dict[str, Any]]):
        """
        Save detected anomalies to database

        Args:
            anomalies (List[Dict]): List of anomaly dictionaries
        """
        for anomaly in anomalies:
            NetworkAnomaly.objects.create(
                type=anomaly["type"],
                description=anomaly["description"],
                severity=anomaly["severity"],
            )


def run_anomaly_detection(time_window_hours: int = 1):
    """
    Run comprehensive anomaly detection

    Args:
        time_window_hours (int): Hours to analyze for anomalies
    """
    try:
        detector = AdvancedAnomalyDetector()
        anomalies = detector.detect_network_anomalies(time_window_hours)
        detector.save_anomalies(anomalies)

        logger.info(f"Detected {len(anomalies)} network anomalies")
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}", exc_info=True)
