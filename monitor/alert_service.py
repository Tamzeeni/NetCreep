import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Alert, AlertThreshold

logger = logging.getLogger(__name__)


def check_threshold(metric, value):
    """Check if a metric value exceeds any thresholds"""
    thresholds = AlertThreshold.objects.filter(metric=metric, enabled=True)

    for threshold in thresholds:
        if value >= threshold.threshold_value:
            create_alert(threshold, value)


def create_alert(threshold, value):
    """Create a new alert and send notification if configured"""
    try:
        # Check if there's already an unresolved alert for this threshold
        existing_alert = Alert.objects.filter(
            threshold=threshold, resolved=False
        ).first()

        if not existing_alert:
            alert = Alert.objects.create(threshold=threshold, triggered_value=value)

            if threshold.email_notification and threshold.notification_email:
                send_alert_email(alert)

            logger.info(f"Created new alert: {alert}")
            return alert

    except Exception as e:
        logger.error(f"Error creating alert: {str(e)}")


def send_alert_email(alert):
    """Send email notification for alert"""
    try:
        subject = f"NetCreep Alert: {alert.threshold.name}"
        message = f"""
Alert Details:
-------------
Metric: {alert.threshold.metric}
Value: {alert.triggered_value}
Threshold: {alert.threshold.threshold_value}
Severity: {alert.threshold.severity}
Time: {alert.triggered_at}

Description: {alert.threshold.description}

Please check  NetCreep dashboard for more details.
"""
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [alert.threshold.notification_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending alert email: {str(e)}")
