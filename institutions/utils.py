from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Institution
from accounts.models import Subscription, UserAffiliation
from helpers.utils import change_member_role, SalesforceAPIError, handle_confirmation_and_subscription
from helpers.emails import  send_hub_admins_account_creation_email
from institutions.models import Institution
from helpers.models import HubActivity
from django.db import transaction
from django.utils import timezone
from localcontexts.utils import dev_prod_or_local


def get_institution(pk):
    return Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)


def handle_institution_creation(request, form, subscription_form ):
    try:
        with transaction.atomic():
            data = form.save(commit=False)
            data.institution_creator = request.user
            data.save()
            response = handle_confirmation_and_subscription(request, subscription_form, data)
            if not response:
                raise SalesforceAPIError("Salesforce account or lead creation failed.")
            affiliation = UserAffiliation.objects.prefetch_related("institutions").get(user=request.user)
            affiliation.institutions.add(data)
            affiliation.save()

            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="New Institution",
                institution_id=data.id,
                action_account_type="institution",
            )
    except SalesforceAPIError as e:
        messages.add_message(
            request,
            messages.ERROR,
            "Something went wrong. Please Try again later."
        )

# This is for retroactively adding ROR IDs to Institutions.
# Currently not being used anywhere.

def set_ror_id(institution):
    import requests

    url = 'https://api.ror.org/organizations'
    query = institution.institution_name
    params = { 'query': query }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            ror_id = data['items'][0]['id']
            institution.ror_id = ror_id
            institution.save()
        else:
            print('No matching institution found.')
    else:
        print('Error:', response.status_code)

def add_user(request, institution, member, current_role, new_role):
    try:
        subscription = Subscription.objects.get(institution=institution)
    except:
        subscription = None

    if new_role not in ('editor', 'administrator', 'admin') and current_role in ('editor', 'administrator', 'admin'):
        change_member_role(institution, member, current_role, new_role)
        if subscription.users_count >= 0:
            subscription.users_count += 1
            subscription.save()
    elif new_role in ('editor', 'administrator', 'admin') and current_role in ('editor', 'administrator', 'admin'):
        change_member_role(institution, member, current_role, new_role)
    elif subscription is not None and (subscription.users_count > 0 or subscription.users_count == -1) and new_role in ('editor', 'administrator', 'admin'):
        change_member_role(institution, member, current_role, new_role)
        if subscription.users_count >= 0:
            subscription.users_count -=1
            subscription.save()
    elif subscription is None:
        messages.add_message(request, messages.ERROR, 
                           'The subscription process of your institution is not completed yet. '
                           'Please wait for the completion of subscription process.')
    else:
        messages.add_message(request, messages.ERROR, 
                            'Your institution has reached its editors and admins limit. '
                            'Please upgrade your subscription plan to add more editors and admins.')
