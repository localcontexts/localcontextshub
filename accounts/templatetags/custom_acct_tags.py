from django import template
from django.db.models import Q

from accounts.utils import get_users_name
from communities.models import Community, JoinRequest
from institutions.models import Institution
from researchers.models import Researcher
from accounts.models import ServiceProviderConnections

register = template.Library()


@register.simple_tag
def all_projects_count(projects):
    return projects.count()


@register.simple_tag
def projects_with_labels_count(projects):
    results = projects.filter(Q(bc_labels__isnull=False) | Q(tk_labels__isnull=False)).distinct()
    return results.count()


@register.simple_tag
def projects_with_notices_count(projects):
    results = projects.filter(project_notice__archived=False).distinct()
    return results.count()


@register.simple_tag
def community_count():
    return Community.approved.count()


@register.simple_tag
def institution_count():
    return Institution.subscribed.count()


@register.simple_tag
def researcher_count():
    return Researcher.objects.filter(is_subscribed=True).count()


@register.simple_tag
def all_account_count():
    c = Community.approved.count()
    i = Institution.subscribed.count()
    r = Researcher.objects.filter(is_subscribed=True).count()
    total = c + i + r
    return total


@register.simple_tag
def otc_registry_count():
    r = Researcher.objects.filter(otc_researcher_url__isnull=False).distinct().count()
    i = Institution.objects.filter(otc_institution_url__isnull=False).distinct().count()
    return r + i


@register.simple_tag
def join_request_inst(institution, user):
    return JoinRequest.objects.filter(institution=institution, user_from=user).exists()


@register.simple_tag
def join_request_comm(community, user):
    return JoinRequest.objects.filter(community=community, user_from=user).exists()


@register.simple_tag
def display_name(user):
    return get_users_name(user)


@register.simple_tag
def is_user_member(account, user):
    if isinstance(account, Institution):
        return account.is_user_in_institution(user)
    if isinstance(account, Community):
        return account.is_user_in_community(user)


@register.simple_tag
def is_connected_service_provider(sp_account, account):
    if isinstance(account, Institution):
        return ServiceProviderConnections.objects.filter(
            institutions=account, service_provider=sp_account).exists()
    if isinstance(account, Community):
        return ServiceProviderConnections.objects.filter(
            communities=account, service_provider=sp_account).exists()
    if isinstance(account, Researcher):
        return ServiceProviderConnections.objects.filter(
            researchers=account, service_provider=sp_account).exists()
