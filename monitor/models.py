from django.db import models
from django.utils import timezone


class NetworkInterface(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PacketCapture(models.Model):
    interface = models.ForeignKey(NetworkInterface, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    protocol = models.CharField(max_length=20)
    source_ip = models.GenericIPAddressField()
    destination_ip = models.GenericIPAddressField()
    source_port = models.IntegerField()
    destination_port = models.IntegerField()
    packet_size = models.IntegerField()
    payload = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.protocol} packet from {self.source_ip}:{self.source_port}"


class AlertThreshold(models.Model):
    name = models.CharField(max_length=100)
    metric = models.CharField(max_length=50)  # e.g., 'packet_count', 'bandwidth'
    threshold_value = models.FloatField()
    severity = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
    )
    description = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=True)
    notification_email = models.EmailField(blank=True, null=True)
    email_notification = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.metric} threshold"


class Alert(models.Model):
    threshold = models.ForeignKey(AlertThreshold, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    current_value = models.FloatField()
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def resolve(self):
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Alert: {self.threshold.name} at {self.timestamp}"


class NetworkPerformanceMetric(models.Model):
    interface = models.ForeignKey(NetworkInterface, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    bytes_sent = models.BigIntegerField()
    bytes_received = models.BigIntegerField()
    packets_sent = models.BigIntegerField()
    packets_received = models.BigIntegerField()
    error_rate = models.FloatField()
    latency = models.FloatField()

    def __str__(self):
        return f"Network Performance: {self.interface.name} at {self.timestamp}"


class NetworkAnomaly(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    interface = models.ForeignKey(NetworkInterface, on_delete=models.CASCADE)
    anomaly_type = models.CharField(max_length=50)
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
    )
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.anomaly_type} anomaly on {self.interface.name}"


class Packet(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    interface = models.ForeignKey(NetworkInterface, on_delete=models.CASCADE)
    protocol = models.CharField(max_length=20)
    source_ip = models.GenericIPAddressField()
    destination_ip = models.GenericIPAddressField()
    source_port = models.IntegerField()
    destination_port = models.IntegerField()
    packet_size = models.IntegerField()
    payload = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.protocol} packet from {self.source_ip}:{self.source_port}"


class SystemStat(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    network_in = models.BigIntegerField()
    network_out = models.BigIntegerField()

    def __str__(self):
        return f"System Stats at {self.timestamp}"
