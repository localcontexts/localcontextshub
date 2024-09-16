from django import template
from django.db.models import Q, Count
from itertools import chain

from accounts.utils import get_users_name
from communities.models import Community, JoinRequest
from institutions.models import Institution
from projects.models import ProjectCreator, Project
from researchers.models import Researcher
from serviceproviders.models import ServiceProvider
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
    if isinstance(account, ServiceProvider):
        return account.is_user_in_service_provider(user)


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


@register.simple_tag
def user_created_project_in_community(user_id: int, community_id: int) -> bool:
    return ProjectCreator.objects.filter(
        community=community_id,
        project__project_creator=user_id
    ).exists()


@register.simple_tag
def user_created_project_in_institution(user_id: int, institution_id: int) -> bool:
    return ProjectCreator.objects.filter(
        institution=institution_id,
        project__project_creator=user_id
    ).exists()


@register.simple_tag
def user_created_project_as_researcher(user_id: int, researcher_id: int) -> bool:
    return ProjectCreator.objects.filter(
        researcher=researcher_id,
        project__project_creator=user_id
    ).exists()


@register.simple_tag
def account_count_cards(account):
    '''
        For Project Lists:
            1. account projects +
            2. projects account has been notified of
            3. projects where account is contributor

        Counts:
            1. Projects with Labels
            2. Projects with Notices
            3. Projects with Connections other than the account itself
    '''

    if isinstance(account, Institution):
        projects_list = list(chain(
            account.institution_created_project.all().values_list(
                'project__unique_id', flat=True
            ),
            account.institutions_notified.all().values_list(
                'project__unique_id', flat=True
            ),
            account.contributing_institutions.all().values_list(
                'project__unique_id', flat=True
            ),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.filter(unique_id__in=project_ids)

        labels_count = projects.filter(
            Q(bc_labels__isnull=False) | Q(tk_labels__isnull=False)
        ).distinct().count()

        notices_count = projects.filter(project_notice__archived=False).distinct().count()

        connections_count = projects.annotate(
                institution_count=Count('project_contributors__institutions'
            )).exclude(
                Q(project_contributors__communities=None) &
                Q(project_contributors__researchers=None) &
                Q(institution_count=1)
            ).distinct().count()

    elif isinstance(account, Researcher):
        projects_list = list(chain(
            account.researcher_created_project.all().values_list(
                'project__unique_id', flat=True
            ),
            account.researchers_notified.all().values_list(
                'project__unique_id', flat=True
            ),
            account.contributing_researchers.all().values_list(
                'project__unique_id', flat=True
            ),
        ))
        project_ids = list(set(projects_list))
        projects = Project.objects.filter(unique_id__in=project_ids)

        labels_count = projects.filter(
            Q(bc_labels__isnull=False) | Q(tk_labels__isnull=False)
        ).distinct().count()

        notices_count = projects.filter(project_notice__archived=False).distinct().count()

        connections_count = projects.annotate(
                researcher_count=Count('project_contributors__researchers'
            )).exclude(
                Q(project_contributors__communities=None) &
                Q(project_contributors__institutions=None) &
                Q(researcher_count=1)
            ).distinct().count()

    elif isinstance(account, Community):
        projects_list = list(chain(
            account.community_created_project.all().values_list(
                'project__unique_id', flat=True
            ),
            account.communities_notified.all().values_list(
                'project__unique_id', flat=True
            ),
            account.contributing_communities.all().values_list(
                'project__unique_id', flat=True
            ),
        ))
        project_ids = list(set(projects_list))
        projects = Project.objects.filter(unique_id__in=project_ids)

        labels_count = projects.filter(
            Q(bc_labels__isnull=False) | Q(tk_labels__isnull=False)
        ).distinct().count()

        notices_count = projects.filter(project_notice__archived=False).distinct().count()

        connections_count = projects.annotate(
                community_count=Count('project_contributors__communities'
            )).exclude(
                Q(project_contributors__researchers=None) &
                Q(project_contributors__institutions=None) &
                Q(community_count=1)
            ).distinct().count()

    elif isinstance(account, ServiceProvider):
        try:
            institutions = ServiceProviderConnections.objects.filter(
                    service_provider=account
                ).annotate(institution_count = Count('institutions')).values_list(
                    'institution_count', flat=True
                ).first()
            communities = ServiceProviderConnections.objects.filter(
                    service_provider=account
                ).annotate(community_count = Count('communities')).values_list(
                    'community_count', flat=True
                ).first()
            researchers = ServiceProviderConnections.objects.filter(
                    service_provider=account
                ).annotate(researcher_count = Count('researchers')).values_list(
                    'researcher_count', flat=True
                ).first()
            connections_count = institutions + communities + researchers

        except:
            connections_count = 0

        return {'connections': connections_count}

    counts = {
        'labels': labels_count,
        'notices': notices_count,
        'connections': connections_count
    }

    return counts
