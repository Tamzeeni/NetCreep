from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Packet(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    summary = models.TextField()
    protocol = models.CharField(max_length=10, default='UNKNOWN')  # TCP, UDP, ICMP, etc.
    src_ip = models.GenericIPAddressField(null=True, blank=True)  # Make nullable
    dst_ip = models.GenericIPAddressField(null=True, blank=True)  # Make nullable
    src_port = models.IntegerField(null=True, blank=True)
    dst_port = models.IntegerField(null=True, blank=True)
    size = models.IntegerField(default=0)  # Default size to 0

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['protocol']),
            models.Index(fields=['src_ip']),
            models.Index(fields=['dst_ip']),
        ]

    def __str__(self):
        return f"{self.timestamp}: {self.protocol} {self.src_ip}:{self.src_port} -> {self.dst_ip}:{self.dst_port}"

        
    @classmethod
    def cleanup_old_packets(cls):
        """Keep only the latest 1000 packets"""
        # Get the timestamp of the 1000th newest packet
        packets = cls.objects.order_by('-timestamp')
        if packets.count() > 1000:
            cutoff_packet = packets[999]  # 0-based index, so 999 is the 1000th packet
            # Delete all packets older than the cutoff
            cls.objects.filter(timestamp__lt=cutoff_packet.timestamp).delete()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Cleanup old packets after saving new one
        self.cleanup_old_packets()


class SystemStat(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    bytes_sent = models.BigIntegerField()
    bytes_recv = models.BigIntegerField()

    def __str__(self):
        return f"SystemStat at {self.timestamp}"


class NetworkAnomaly(models.Model):
    SEVERITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=100)
    description = models.TextField()
    severity = models.CharField(max_length=6, choices=SEVERITY_CHOICES)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type} - {self.timestamp}"


class AlertThreshold(models.Model):
    METRIC_CHOICES = [
        ('cpu_usage', 'CPU Usage'),
        ('memory_usage', 'Memory Usage'),
        ('disk_usage', 'Disk Usage'),
        ('network_traffic', 'Network Traffic'),
        ('port_scan', 'Port Scan Detection'),
        ('high_traffic_ip', 'High Traffic IP')
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ]

    name = models.CharField(max_length=100)
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES)
    threshold_value = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    enabled = models.BooleanField(default=True)
    email_notification = models.BooleanField(default=False)
    notification_email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.metric})"

class Alert(models.Model):
    threshold = models.ForeignKey(AlertThreshold, on_delete=models.CASCADE)
    triggered_value = models.FloatField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.CharField(max_length=100, blank=True, null=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-triggered_at']

    def __str__(self):
        return f"{self.threshold.name} - {self.triggered_at}"