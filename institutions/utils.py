from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Institution
from helpers.utils import create_salesforce_account_or_lead
from django.contrib import messages
from accounts.models import Subscription
from helpers.utils import change_member_role
from helpers.emails import send_hub_admins_application_email
from institutions.models import Institution

def get_institution(pk):
    return Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

# This is for retroactively adding ROR IDs to Institutions.
# Currently not being used anywhere.

def handle_confirmation_and_subscription(request, subscription_form, institution):
    first_name = subscription_form.cleaned_data["first_name"]
    join_flag = False
    if not subscription_form.cleaned_data["last_name"]:
        subscription_form.cleaned_data["last_name"] = first_name
    try:
        response = confirm_subscription(request, institution, join_flag, subscription_form)
        data = Institution.objects.get(institution_name=institution.institution_name)
        send_hub_admins_application_email(request, institution, data)
        return response
    except:
        messages.add_message(
            request,
            messages.ERROR,
            "An unexpected error has occurred. Please contact support@localcontexts.org.",
        )
        return redirect("dashboard")    

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
        
def confirm_subscription(request, institution, join_flag, form):
    if institution.institution_creator == request.user._wrapped:
        if create_salesforce_account_or_lead(hubId=str(institution.id)+"_i", data=form.cleaned_data):
            institution.is_submitted = True
            institution.save()
            messages.add_message(request, messages.INFO, 'Thank you for your submission, our team will review and be in contact with the subscription contract. You will be notified once your subscription has been processed.')
        else:
            messages.add_message(request, messages.ERROR, 'An unexpected error has occurred. Please contact support@localcontexts.org.')
        return redirect('dashboard')
    elif request.user._wrapped not in institution.get_admins():
        join_flag = True
        return render(request, 'accounts/confirm-subscription.html', {'form': form, 'account':institution, "subscription_url": 'confirm-subscription-institution', 'join_flag':join_flag,})

def add_user(request, institution, member, current_role, new_role):
    subscription = Subscription.objects.get(institution=institution)
    if new_role not in ('editor', 'administrator', 'admin') and current_role in ('editor', 'administrator', 'admin'):
        change_member_role(institution, member, current_role, new_role)
        if subscription.users_count >= 0:
            subscription.users_count += 1
            subscription.save()
    elif new_role in ('editor', 'administrator', 'admin') and current_role in ('editor', 'administrator', 'admin'):
        change_member_role(institution, member, current_role, new_role)
    elif (subscription.users_count > 0 or subscription.users_count == -1) and new_role in ('editor', 'administrator', 'admin'):
        change_member_role(institution, member, current_role, new_role)
        if subscription.users_count >= 0:
            subscription.users_count -=1
            subscription.save()
    else:
        messages.add_message(request, messages.ERROR, 
                            'Your institution has reached its editors and admins limit. '
                            'Please upgrade your subscription plan to add more editors and admins.')

         
def check_subscription(request, institution):
    redirection = False
    try:
        subscription = Subscription.objects.get(institution=institution)
    except Subscription.DoesNotExist:
        redirection = True

    return redirection