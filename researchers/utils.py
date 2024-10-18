from .models import Researcher
from helpers.utils import handle_confirmation_and_subscription
from helpers.emails import (send_researcher_email, send_hub_admins_account_creation_email,
                            manage_researcher_mailing_list)
from helpers.models import HubActivity
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect


def is_user_researcher(user):
    if Researcher.objects.filter(user=user).exists():
        return Researcher.objects.select_related('user').get(user=user)
    else:
        return None


def checkif_user_researcher(current_researcher, user):
    if Researcher.objects.filter(user=user).exists():
        researcher = Researcher.objects.select_related('user').get(user=user)
        if current_researcher == researcher:
            return True
        else:
            return False
    else:
        return False


def handle_researcher_creation(request, subscription_form, form, orcid_id, orcid_token, env):
    try:
        with transaction.atomic():
            data = form.save(commit=False)
            data.user = request.user
            data.orcid_auth_token = orcid_token
            data.orcid = orcid_id
            data.save()
            handle_confirmation_and_subscription(request, subscription_form, data, env)

            # Mark current user as researcher
            request.user.user_profile.is_researcher = True
            request.user.user_profile.save()

            if env != 'SANDBOX':
                # sends one email to the account creator
                # and one to either site admin or support
                send_researcher_email(request)
                send_hub_admins_account_creation_email(request, data)

                # Add researcher to mailing list
                if env == 'PROD':
                    manage_researcher_mailing_list(request.user.email, True)

            # Adds activity to Hub Activity
            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="New Researcher"
            )
    except Exception as e:
        messages.add_message(
            request,
            messages.ERROR,
            f"An unexpected error occured: {str(e)}"
            " Please contact support@localcontexts.org."
        )
        return redirect('dashboard')
