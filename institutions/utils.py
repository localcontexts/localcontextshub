from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Institution
from helpers.utils import create_salesforce_account_or_lead
from django.contrib import messages
from accounts.models import Subscription
from helpers.utils import change_member_role

def get_institution(pk):
    return Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

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
        
def confirm_subscription(request, institution, join_flag, form):
    if institution.institution_creator == request.user._wrapped:
        if create_salesforce_account_or_lead(hubId=str(institution.id)+"_i", data=form.cleaned_data):
            institution.is_submitted = True
            institution.save()
            messages.add_message(request, messages.INFO, 'Thank you for your submission, our team will review and be in contact with the subscription contact. You will be notified once your subscription has been processed.')
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
        subscription.users_count += 1
        subscription.save()
    elif new_role in ('editor', 'administrator', 'admin') and current_role in ('editor', 'administrator', 'admin'):
        change_member_role(institution, member, current_role, new_role)
    elif subscription.users_count > 0 and new_role in ('editor', 'administrator', 'admin'):
        change_member_role(institution, member, current_role, new_role)
        subscription.users_count -=1
        subscription.save()
    else:
        messages.add_message(request, messages.ERROR, 
                            'Your institution has reached its editors and admins limit. '
                            'Please upgrade your subscription plan to add more editors and admins.')

def notification_condition(request, notification_count, communities_selected):
    if notification_count < len(communities_selected):
        remaining_notifications = len(communities_selected) - notification_count
        if notification_count == 1 and remaining_notifications == 1:
            messages.add_message(request, messages.INFO, f'You have successfully notified {notification_count} community. {remaining_notifications} community could not be notified due to subscription limit. Please upgrade your subscription plan to notify more communities.')
        elif notification_count == 1:
            messages.add_message(request, messages.INFO, f'You have successfully notified {notification_count} community. {remaining_notifications} communities could not be notified due to subscription limit. Please upgrade your subscription plan to notify more communities.')
        elif remaining_notifications == 1:
            messages.add_message(request, messages.INFO, f'You have successfully notified {notification_count} communities. {remaining_notifications} community could not be notified due to subscription limit. Please upgrade your subscription plan to notify more communities.')
        else:
            messages.add_message(request, messages.INFO, f'You have successfully notified {notification_count} communities. {remaining_notifications} communities could not be notified due to subscription limit. Please upgrade your subscription plan to notify more communities.')
    else:
        if notification_count == 1:
            messages.add_message(request, messages.INFO, f'You have successfully notified {notification_count} community.')
        else:
            messages.add_message(request, messages.INFO, f'You have successfully notified {notification_count} communities.')
            
def check_subscription(request, institution):
    redirection = False
    try:
        subscription = Subscription.objects.get(institution=institution)
    except Subscription.DoesNotExist:
        redirection = True

    return redirection