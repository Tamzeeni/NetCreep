document.addEventListener('DOMContentLoaded', function() {
    const emailNotificationCheckbox = document.getElementById('email_notification');
    const notificationEmailField = document.getElementById('notification_email_field');

    function toggleEmailField() {
        const emailFieldContainer = notificationEmailField.parentElement;
        if (emailNotificationCheckbox.checked) {
            emailFieldContainer.style.display = 'block';
            notificationEmailField.required = true;
        } else {
            emailFieldContainer.style.display = 'none';
            notificationEmailField.required = false;
            notificationEmailField.value = '';
        }
    }

    // Initial state
    toggleEmailField();

    // Listen for changes
    emailNotificationCheckbox.addEventListener('change', toggleEmailField);
});