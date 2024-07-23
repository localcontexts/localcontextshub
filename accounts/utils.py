from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render, redirect
from django.urls import reverse

from django.conf import settings
from django.contrib import messages

from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from serviceproviders.models import ServiceProvider
from unidecode import unidecode


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
            unidecode(obj.community_name.lower().strip())
            if isinstance(obj, Community)
            else (
                unidecode(obj.institution_name.lower().strip())
                if isinstance(obj, Institution)
                else (
                    unidecode(obj.name.lower().strip())
                    if isinstance(obj, ServiceProvider)
                    else (
                        unidecode(obj.user.first_name.lower().strip())
                        if isinstance(obj, Researcher)
                        and obj.user.first_name.strip()
                        else (
                            unidecode(obj.user.username.lower().strip())
                            if isinstance(obj, Researcher)
                            else ""
                        )
                    )
                )
            )
        ),
    )

    return cards


def get_next_path(request, default_path: str):
    next_path = request.POST.get("next")

    # validate next_path exists and is not an open redirect
    if next_path and url_has_allowed_host_and_scheme(
        next_path, settings.ALLOWED_HOSTS
    ):
        return next_path

    return default_path


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
            "Thank you for your submission, our team will review and be in "
            "contact with the subscription contract. You will be notified "
            "once your subscription has been processed.",
        )
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "An unexpected error has occurred."
            " Please contact support@localcontexts.org.")

    return redirect('dashboard')
