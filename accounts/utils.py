from typing import Union, Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render, redirect
from django.urls import reverse
from unidecode import unidecode
from django.contrib import messages

from accounts.models import UserAffiliation
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from serviceproviders.models import ServiceProvider


def get_users_name(user):
    if user:
        return user.get_full_name() or user.username
    return None


def manage_mailing_list(request, first_name, emailb64):
    selections = request.POST.getlist("topic")
    tech = "no"
    news = "no"
    events = "no"
    notice = "no"
    labels = "no"
    for item in selections:
        if item == "tech":
            tech = "yes"
        if item == "news":
            news = "yes"
        if item == "events":
            events = "yes"
        if item == "notice":
            notice = "yes"
        if item == "labels":
            labels = "yes"
    variables = (
        '{"first_name":"%s", "tech": "%s", "news": "%s", '
        '"events": "%s","notice": "%s","labels": "%s", '
        '"id": "%s"}'
        % (first_name, tech, news, events, notice, labels, emailb64)
    )
    return variables


def return_registry_accounts(
            community_accounts, researcher_accounts, institution_accounts,
            service_provider_accounts
        ):

    combined_accounts = []

    if community_accounts is not None:
        combined_accounts.extend(community_accounts)

    combined_accounts.extend(researcher_accounts)
    combined_accounts.extend(institution_accounts)
    combined_accounts.extend(service_provider_accounts)

    cards = sorted(
        combined_accounts,
        key=lambda obj: (
            unidecode(obj.community_name.lower().strip()) if isinstance(obj, Community) else
            unidecode(obj.institution_name.lower().strip()) if isinstance(obj, Institution) else
            unidecode(obj.name.lower().strip()) if isinstance(obj, ServiceProvider) else
            (
                unidecode(obj.user.first_name.lower().strip())
                if isinstance(obj, Researcher) and obj.user.first_name.strip() else
                unidecode(obj.user.username.lower().strip()) if isinstance(obj, Researcher)
                else ''
            )
        )
    )

    return cards


def get_next_path(request, default_path: str):
    next_path = request.POST.get("next")

    # validate next_path exists and is not an open redirect
    if next_path and url_has_allowed_host_and_scheme(next_path, settings.ALLOWED_HOSTS):
        return next_path

    return default_path


def remove_user_from_account(
    user: User,
    account: Optional[Union[Community, Institution]] = None
) -> None:
    """Removes the user from a specific community or institution account,
    or from all affiliated accounts if no specific account is provided.

    Args:
        user: The user object.
        account: A specific community or institution account. If not provided,
                 the user will be removed from all affiliated accounts.

    Returns:
        None

    Example usage:
     # Remove the user from a specific community
        remove_user_from_account(user, specific_community)
     # Remove the user from all affiliated accounts (communities and institutions)
        remove_user_from_account(user)
    """

    # Fetch the user's affiliation
    affiliation = UserAffiliation.objects.prefetch_related(
        'communities', 'institutions'
    ).get(user=user)

    if account:
        # Remove the user from the specific account provided
        if user in account.admins.all():
            account.admins.remove(user)
        if user in account.editors.all():
            account.editors.remove(user)
        if user in account.viewers.all():
            account.viewers.remove(user)

        # Remove the account from the user's affiliations
        if isinstance(account, Community):
            affiliation.communities.remove(account)
        elif isinstance(account, Institution):
            affiliation.institutions.remove(account)

    else:
        # No specific account provided, so remove the user from all affiliated accounts
        accounts = list(affiliation.communities.all()) + list(affiliation.institutions.all())

        for acc in accounts:
            if user in acc.admins.all():
                acc.admins.remove(user)
            if user in acc.editors.all():
                acc.editors.remove(user)
            if user in acc.viewers.all():
                acc.viewers.remove(user)

            if isinstance(acc, Community):
                affiliation.communities.remove(acc)
            elif isinstance(acc, Institution):
                affiliation.institutions.remove(acc)


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


def institute_account_subscription(
    request, institution, account_exist, form, non_ror_institutes
):
    from helpers.utils import create_salesforce_account_or_lead

    if institution and account_exist:
        if institution.institution_creator == account_exist:
            messages.add_message(
                request,
                messages.INFO,
                "Your Account already exists on Hub. Please login.",
            )
            return redirect("dashboard")
        elif account_exist and institution:
            next_url = reverse(
                "public-institution", kwargs={"pk": institution.id}
            )
            login_url = f"/login/?next={next_url}"
            return render(
                request,
                "accounts/subscription-inquiry.html",
                {
                    "form": form,
                    "login_url": login_url,
                    "institution": institution,
                },
            )
    elif account_exist and not institution:
        messages.add_message(
            request,
            messages.INFO,
            "Your Account already exists on Hub. "
            "Please login to create the insitute.",
        )
        return redirect("select-account")
    elif institution and not account_exist:
        return render(
            request,
            "accounts/subscription-inquiry.html",
            {
                "form": form,
                "non_ror_institutes": non_ror_institutes,
                "institution": institution,
            },
        )
    else:
        if create_salesforce_account_or_lead(request, data=form.cleaned_data):
            messages.add_message(
                request,
                messages.INFO,
                (
                    "Thank you for your submission, "
                    "our team will review and be in "
                    "contact with the subscription contact. "
                    "You will be notified once your "
                    "subscription has been processed."
                ),
            )
            return redirect("subscription-inquiry")
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "An unexpected error has occurred. "
                "Please contact support@localcontexts.org.",
            )
            return redirect("subscription-inquiry")


def confirm_subscription(request, user, form, account_type):
    from helpers.utils import create_salesforce_account_or_lead
    if account_type == "institution_account":
        hub_id = str(user.id) + "_i"
        isbusiness = True
    elif account_type == "researcher_account":
        hub_id = str(user.id) + "_r"
        isbusiness = False
    elif account_type == "service_provider_account":
        hub_id = str(user.id) + "_sp"
        isbusiness = True
    else:
        raise ValueError("Invalid account type")

    if create_salesforce_account_or_lead(
        request,
        hubId=hub_id,
        data=form.cleaned_data,
        isbusiness=isbusiness
    ):
        messages.add_message(
            request,
            messages.INFO,
            "Thank you for your interest! Our team will review and be in contact soon."
        )
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "An unexpected error has occurred."
            " Please contact support@localcontexts.org.")

    return redirect('dashboard')


def escape_single_quotes(data):
    if isinstance(data, dict):
        return {key: escape_single_quotes(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [escape_single_quotes(item) for item in data]
    elif isinstance(data, str):
        return data.replace("'", "\\'")
    return data
