from .models import Researcher
from django.contrib import messages
from django.shortcuts import redirect
from helpers.utils import create_salesforce_account_or_lead

def is_user_researcher(user):
    if Researcher.objects.filter(user=user).exists():
        return Researcher.objects.select_related('user').get(user=user)
    else:
        return None

def confirm_subscription(request, researcher, join_flag, form):
    if create_salesforce_account_or_lead(hubId=str(researcher.id)+"_r", data=form.cleaned_data):
        researcher.is_subscribed = True
        researcher.save()
        messages.add_message(request, messages.INFO, 'Thank you for your submission, our team will review and be in contact with the subscription contact. You will be notified once your subscription has been processed.')
    else:
        messages.add_message(request, messages.ERROR, 'An unexpected error has occurred. Please contact support@localcontexts.org.')
    return redirect('dashboard')

def checkif_user_researcher(current_researcher, user):
    if Researcher.objects.filter(user=user).exists():
        researcher = Researcher.objects.select_related('user').get(user=user)
        if current_researcher == researcher:
            return True
        else:
            return False
    else:
        return False