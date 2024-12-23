# Generated by Django 5.0 on 2024-12-03 03:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AlertThreshold",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("metric", models.CharField(max_length=50)),
                ("threshold_value", models.FloatField()),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("critical", "Critical"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Optional description of the alert threshold conditions",
                        null=True,
                    ),
                ),
                ("enabled", models.BooleanField(default=True)),
                (
                    "notification_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                ("email_notification", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="NetworkInterface",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Optional description of the network interface",
                        null=True,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="SystemStat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("cpu_usage", models.FloatField()),
                ("memory_usage", models.FloatField()),
                ("disk_usage", models.FloatField()),
                ("network_in", models.BigIntegerField()),
                ("network_out", models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Alert",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("current_value", models.FloatField()),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Detailed description of the alert",
                        null=True,
                    ),
                ),
                ("is_resolved", models.BooleanField(default=False)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "threshold",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="monitor.alertthreshold",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NetworkAnomaly",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "anomaly_type",
                    models.CharField(
                        default="unknown",
                        help_text="Type of network anomaly detected",
                        max_length=50,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Detailed description of the network anomaly",
                        null=True,
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("critical", "Critical"),
                        ],
                        default="low",
                        max_length=20,
                    ),
                ),
                ("is_resolved", models.BooleanField(default=False)),
                (
                    "interface",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="monitor.networkinterface",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NetworkPerformanceMetric",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("bytes_sent", models.BigIntegerField()),
                ("bytes_received", models.BigIntegerField()),
                ("packets_sent", models.BigIntegerField()),
                ("packets_received", models.BigIntegerField()),
                ("error_rate", models.FloatField()),
                ("latency", models.FloatField()),
                (
                    "interface",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="monitor.networkinterface",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Packet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("protocol", models.CharField(max_length=20)),
                ("source_ip", models.GenericIPAddressField()),
                ("destination_ip", models.GenericIPAddressField()),
                ("source_port", models.IntegerField()),
                ("destination_port", models.IntegerField()),
                ("packet_size", models.IntegerField()),
                ("payload", models.TextField(blank=True, null=True)),
                (
                    "interface",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="monitor.networkinterface",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PacketCapture",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("protocol", models.CharField(max_length=20)),
                ("source_ip", models.GenericIPAddressField()),
                ("destination_ip", models.GenericIPAddressField()),
                ("source_port", models.IntegerField()),
                ("destination_port", models.IntegerField()),
                ("packet_size", models.IntegerField()),
                ("payload", models.TextField(blank=True, null=True)),
                (
                    "interface",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="monitor.networkinterface",
                    ),
                ),
            ],
        ),
    ]
