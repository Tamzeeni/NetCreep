from django import forms

from .models import AlertThreshold


class AlertThresholdForm(forms.ModelForm):
    class Meta:
        model = AlertThreshold
        fields = [
            "name",
            "metric",
            "threshold_value",
            "severity",
            "enabled",
            "email_notification",
            "notification_email",
            "description",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter threshold name"}
            ),
            "metric": forms.Select(attrs={"class": "form-control"}),
            "threshold_value": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "max": "100", "step": "0.1"}
            ),
            "severity": forms.Select(attrs={"class": "form-control"}),
            "enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "email_notification": forms.CheckboxInput(
                attrs={"class": "form-check-input", "id": "email_notification"}
            ),
            "notification_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter email for notifications",
                    "id": "notification_email_field",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter description for this alert threshold",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        email_notification = cleaned_data.get("email_notification")
        notification_email = cleaned_data.get("notification_email")

        if email_notification and not notification_email:
            raise forms.ValidationError(
                "Email address is required when email notification is enabled."
            )

        threshold_value = cleaned_data.get("threshold_value")
        if threshold_value is not None:
            if threshold_value < 0 or threshold_value > 100:
                raise forms.ValidationError(
                    "Threshold value must be between 0 and 100."
                )

        return cleaned_data

    class Media:
        js = ("js/alert_threshold_form.js",)
