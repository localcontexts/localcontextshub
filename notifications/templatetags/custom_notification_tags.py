from django import template
from django.contrib.auth.models import User

from communities.models import Community
from institutions.models import Institution
from notifications.models import ActionNotification, UserNotification
from researchers.models import Researcher
from serviceproviders.models import ServiceProvider

register = template.Library()


@register.simple_tag
def unread_notifications_exist(account):
    if account is not None:
        if isinstance(account, User):
            return UserNotification.objects.filter(to_user=account, viewed=False).exists()

        if isinstance(account, Researcher):
            return ActionNotification.objects.filter(researcher=account, viewed=False).exists()

        if isinstance(account, Institution):
            return ActionNotification.objects.filter(institution=account, viewed=False).exists()

        if isinstance(account, Community):
            return ActionNotification.objects.filter(community=account, viewed=False).exists()

        if isinstance(account, ServiceProvider):
            return ActionNotification.objects.filter(service_provider=account, viewed=False).exists()

        return False


@register.simple_tag
def return_notifications(account):
    if account is not None:
        if isinstance(account, User):
            return UserNotification.objects.filter(to_user=account)

        if isinstance(account, Researcher):
            return ActionNotification.objects.filter(researcher=account)

        if isinstance(account, Institution):
            return ActionNotification.objects.filter(institution=account)

        if isinstance(account, Community):
            return ActionNotification.objects.filter(community=account)

        if isinstance(account, ServiceProvider):
            return ActionNotification.objects.filter(service_provider=account)

        return None
