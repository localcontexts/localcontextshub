from django.db import models
from django.contrib.auth.models import User
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from serviceproviders.models import ServiceProvider

class UserNotification(models.Model):
    TYPES = (
        ('Welcome', 'welcome'),
        ('Invitation', 'invitation'),
        ('Request', 'request'),
        ('Approval', 'approval'),
        ('Accept', 'accept'),
        ('Remove', 'remove'),
    )

    ROLES = (
        ('Admin', 'admin'),
        ('Editor', 'editor'),
        ('Viewer', 'viewer'),
    )

    title = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="to_user", blank=True)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="from_user", blank=True)
    notification_type = models.CharField(max_length=10, choices=TYPES, null=True, blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=8, choices=ROLES, null=True, blank=True)
    reference_id = models.CharField(max_length=20, null=True, blank=True)
    viewed = models.BooleanField(default=False, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.notification_type}-{self.title}"

    class Meta:
        verbose_name = 'User Notification'
        verbose_name_plural = 'User Notifications'
        ordering = ('viewed', '-created') # will display False first, then True

class ActionNotification(models.Model):
    TYPES = (
        ('Labels', 'labels'),
        ('Connections', 'connections'),
        ('Activity', 'activity'),
        ('Projects', 'projects'),
        ('Members', 'members'),
    )

    title = models.CharField(max_length=200, blank=True)
    notification_type = models.CharField(max_length=20, choices=TYPES, null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="notification_sender", blank=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    researcher = models.ForeignKey(Researcher, on_delete=models.CASCADE, null=True, blank=True)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, null=True, blank=True)
    reference_id = models.CharField(max_length=50, null=True, blank=True)
    viewed = models.BooleanField(default=False, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.notification_type} - {self.title}"

    class Meta:
        verbose_name = 'Action Notification'
        verbose_name_plural = 'Action Notifications'
        ordering = ('viewed', '-created')



