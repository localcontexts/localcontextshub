from django import template

from django.db.models import Count
from accounts.models import ServiceProviderConnections
from helpers.models import OpenToCollaborateNoticeURL


register = template.Library()


# Count of Accounts connected to Service Provider
@register.simple_tag
def connections_count(service_provider):
    institutions = ServiceProviderConnections.objects.filter(
            service_provider=service_provider
        ).annotate(institution_count = Count('institutions')).values_list(
            'institution_count', flat=True
        ).first()
    communities = ServiceProviderConnections.objects.filter(
            service_provider=service_provider
        ).annotate(community_count = Count('communities')).values_list(
            'community_count', flat=True
        ).first()
    researchers = ServiceProviderConnections.objects.filter(
            service_provider=service_provider
        ).annotate(researcher_count = Count('researchers')).values_list(
            'researcher_count', flat=True
        ).first()
    totals = institutions + communities + researchers

    return totals
