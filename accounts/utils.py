from typing import Union

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme
from unidecode import unidecode

from accounts.models import UserAffiliation
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher


def get_users_name(user):
    if user:
        return user.get_full_name() or user.username
    return None


def manage_mailing_list(request, first_name, emailb64):
    selections = request.POST.getlist('topic')
    tech = 'no'
    news = 'no'
    events = 'no'
    notice = 'no'
    labels = 'no'
    for item in selections:
        if item == 'tech':
            tech = 'yes'
        if item == 'news':
            news = 'yes'
        if item == 'events':
            events = 'yes'
        if item == 'notice':
            notice = 'yes'
        if item == 'labels':
            labels = 'yes'
    variables = '{"first_name":"%s", "tech": "%s", "news": "%s", ' \
                '"events": "%s","notice": "%s","labels": "%s", ' \
                '"id": "%s"}' % (
                    first_name, tech, news, events, notice, labels, emailb64)
    return variables


def return_registry_accounts(community_accounts, researcher_accounts, institution_accounts):
    combined_accounts = []

    if community_accounts is not None:
        combined_accounts.extend(community_accounts)

    combined_accounts.extend(researcher_accounts)
    combined_accounts.extend(institution_accounts)

    cards = sorted(
        combined_accounts,
        key=lambda obj: (
            unidecode(obj.community_name.lower().strip())
            if isinstance(obj, Community) else unidecode(obj.institution_name.lower().strip())
            if isinstance(obj, Institution) else unidecode(obj.user.first_name.lower().strip())
            if isinstance(obj, Researcher) and obj.user.first_name.strip() else
            unidecode(obj.user.username.lower().strip()) if isinstance(obj, Researcher) else ''
        )
    )

    return cards


def get_next_path(request, default_path: str):
    next_path = request.POST.get('next')

    # validate next_path exists and is not an open redirect
    if next_path and url_has_allowed_host_and_scheme(next_path, settings.ALLOWED_HOSTS):
        return next_path

    return default_path


def remove_user_from_account_and_account_from_user_affiliations(
        user: User,
        account: Union[Community, Institution]
) -> None:
    """Removes user from account and account from that user's affiliations

    Args:
        user: The user object.
        account: A community or institution account.

    Returns:
        None
    """
    # remove user from account
    if user in account.admins.all():
        account.admins.remove(user)
    if user in account.editors.all():
        account.editors.remove(user)
    if user in account.viewers.all():
        account.viewers.remove(user)

    # remove account from user affiliations
    if type(account) == Community:
        affiliation = UserAffiliation.objects.prefetch_related('communities').get(user=user)
        affiliation.communities.remove(account)
    elif type(account) == Institution:
        affiliation = UserAffiliation.objects.prefetch_related('institutions').get(user=user)
        affiliation.institutions.remove(account)


def dissociates_user_from_affiliated_communities_and_institutions(
        user: User, affiliation: UserAffiliation
) -> None:
    """Separates user from affiliated community and institution accounts.
       After this has completed, both the user and their community/institution accounts
       will still exist. However, they will no longer be associated with each other.

    Args:
        user: The user object.
        affiliation: A UserAffiliation

    Returns:
        None
    """
    for community in affiliation.communities.all():
        remove_user_from_account_and_account_from_user_affiliations(user, community)

    for institution in affiliation.institutions.all():
        remove_user_from_account_and_account_from_user_affiliations(user, institution)


def determine_user_role(user: User) -> str:
    from projects.models import ProjectCreator  # import here to resolve circular imports
    is_account_creator = Researcher.objects.filter(user=user).exists() or \
                         Community.objects.filter(community_creator=user).exists() or \
                         Institution.objects.filter(institution_creator=user).exists() # noqa

    is_project_creator = ProjectCreator.objects.filter(
        project__project_creator__id=user.id
    ).exists()
    if is_account_creator or is_project_creator:
        return 'is_creator_or_project_creator'

    is_member = Community.objects.filter(admins__id__contains=user.id).exists() or \
                Community.objects.filter(editors__id__contains=user.id).exists() or \
                Community.objects.filter(viewers__id__contains=user.id).exists() or \
                Institution.objects.filter(admins__id__contains=user.id).exists() or \
                Institution.objects.filter(editors__id__contains=user.id).exists() or \
                Institution.objects.filter(viewers__id__contains=user.id).exists()  # noqa

    if is_member > 0:
        return 'is_member'

    return 'default'
