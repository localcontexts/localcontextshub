from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from .models import ServiceProvider
from accounts.models import Subscription, UserAffiliation
from helpers.utils import change_member_role, SalesforceAPIError, create_salesforce_account_or_lead
from helpers.emails import send_hub_admins_account_creation_email
from institutions.models import Institution
from helpers.models import HubActivity
from accounts.forms import UserCreateProfileForm, SubscriptionForm
from django.db import transaction


def form_initiation(request):
    subscription_form = SubscriptionForm()

    fields_to_update = {
        "first_name": request.user._wrapped.first_name,
        "last_name": request.user._wrapped.last_name,
    }
    user_form = UserCreateProfileForm(request.POST or None, initial=fields_to_update)
    exclude_choices = {"member", "cc_only"}
    
    modified_inquiry_type_choices = [
        choice
        for choice in SubscriptionForm.INQUIRY_TYPE_CHOICES
        if choice[0] not in exclude_choices
    ]
    subscription_form.fields["inquiry_type"].choices = modified_inquiry_type_choices
    for field, value in fields_to_update.items():
        if value:
            user_form.fields[field].widget.attrs.update({"class": "w-100 readonly-input"})
        
    return  user_form,subscription_form

def handle_service_provider_creation(request, form, subscription_form ):
    try:
        with transaction.atomic():
            data = form.save(commit=False)
            data.account_creator = request.user
            data.save()
            response = handle_confirmation_and_subscription(request, subscription_form, data)
            if not response:
                raise SalesforceAPIError("Salesforce account or lead creation failed.")
            affiliation = UserAffiliation.objects.prefetch_related("service_provider").get(user=request.user)
            affiliation.service_provider.add(data)
            affiliation.save()

            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="New Service Provider",
                service_provider_id=data.id,
                action_account_type="service_provider",
            )
    except SalesforceAPIError as e:
        messages.add_message(
            request,
            messages.ERROR,
            "Something went wrong. Please Try again later."
        )

def handle_confirmation_and_subscription(request, subscription_form, service_provider):
    first_name = subscription_form.cleaned_data["first_name"]
    join_flag = False
    if not subscription_form.cleaned_data["last_name"]:
        subscription_form.cleaned_data["last_name"] = first_name
    response = confirm_subscription(request, service_provider, join_flag, subscription_form)
    data = ServiceProvider.objects.get(name=service_provider.name)
    send_hub_admins_account_creation_email(request, data)
    return response

def confirm_subscription(request, service_provider, join_flag, form):
    if service_provider.account_creator == request.user._wrapped:
        if create_salesforce_account_or_lead(request, hubId=str(service_provider.id)+"_sp", data=form.cleaned_data):
            service_provider.is_submitted = True
            service_provider.save()
            messages.add_message(request, messages.INFO, 'Thank you for your submission, our team will review and be in contact with the subscription contract. You will be notified once your subscription has been processed.')
        else:
            messages.add_message(request, messages.ERROR, 'An unexpected error has occurred. Please contact support@localcontexts.org.')
        return redirect('dashboard')
    elif request.user._wrapped not in service_provider.get_admins():
        join_flag = True
        return render(request, 'accounts/confirm-subscription.html', {'form': form, 'account':service_provider, "subscription_url": 'confirm-subscription-service-provider', 'join_flag':join_flag,})