from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from helpers.models import HubActivity
from accounts.models import UserAffiliation
from .models import ServiceProvider
from helpers.utils import handle_confirmation_and_subscription


def handle_service_provider_creation(request, form, subscription_form, env):
    try:
        with transaction.atomic():
            data = form.save(commit=False)
            data.account_creator = request.user
            data.save()
            if env != 'SANDBOX':
                handle_confirmation_and_subscription(request, subscription_form, data, env)
            affiliation = UserAffiliation.objects.prefetch_related("service_providers").get(user=request.user)
            affiliation.service_providers.add(data)
            affiliation.save()

            # HubActivity.objects.create(
            #     action_user_id=request.user.id,
            #     action_type="New Service Provider",
            #     service_provider_id=data.id,
            #     action_account_type="service_provider",
            # )
    except Exception as e:
        messages.add_message(
            request,
            messages.ERROR,
            "An unexpected error has occurred here."
            " Please contact support@localcontexts.org.",
        )
        return redirect('dashboard')

def get_service_provider(pk):
    return ServiceProvider.objects.select_related('account_creator').get(id=pk)