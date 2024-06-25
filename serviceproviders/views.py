from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.db.models import Q
from itertools import chain
from django.shortcuts import get_object_or_404

from localcontexts.utils import dev_prod_or_local
from projects.utils import *
from helpers.utils import *
from notifications.utils import *
from .utils import *

from .models import *
from projects.models import *
from communities.models import Community, JoinRequest
from notifications.models import ActionNotification
from helpers.models import *
from api.models import AccountAPIKey

from django.contrib.auth.models import User
from accounts.models import UserAffiliation, Subscription

from projects.forms import *
from helpers.forms import (
    ProjectCommentForm,
    OpenToCollaborateNoticeURLForm,
    CollectionsCareNoticePolicyForm,
)
from communities.forms import InviteMemberForm, JoinRequestForm
from accounts.forms import (
    ContactOrganizationForm,
    SignUpInvitationForm,
    SubscriptionForm,
    UserCreateProfileForm,
)
from api.forms import APIKeyGeneratorForm
from .forms import *

from helpers.emails import *
from maintenance_mode.decorators import force_maintenance_mode_off
from django.db import transaction

@login_required(login_url="login")
def preparation_step(request):
    if dev_prod_or_local(request.get_host()) == "SANDBOX":
        return redirect("create-service-provider")
    else:
        service_provider = True
        return render(
            request, "accounts/preparation.html", {"service_provider": service_provider}
        )

@login_required(login_url="login")
def create_service_provider(request):
    form = CreateServiceProviderForm()
    user_form,subscription_form  = form_initiation(request)

    if request.method == "POST":
        form = CreateServiceProviderForm(request.POST)
        if (form.is_valid() and user_form.is_valid() and 
        validate_recaptcha(request)):
            mutable_post_data = request.POST.copy()
            subscription_data = {
            "first_name": user_form.cleaned_data['first_name'],
            "last_name": user_form.cleaned_data['last_name'],
            "email": request.user._wrapped.email,
            "account_type": "service_provider_account",
            "organization_name": form.cleaned_data['name'],
            }
            
            mutable_post_data.update(subscription_data)
            subscription_form = SubscriptionForm(mutable_post_data)
            if subscription_form.is_valid():
                handle_service_provider_creation(request, form, subscription_form)
                return redirect('dashboard')
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Something went wrong. Please Try again later.",
                )
                return redirect('dashboard')
    return render(
        request,
        "serviceproviders/create-service-provider.html",
        {
            "form": form,
            "subscription_form": subscription_form,
            "user_form": user_form,
        },
    )


def public_service_provider_view(request, pk):
    try:
        environment = dev_prod_or_local(request.get_host())
        service_provider = ServiceProvider.objects.get(id=pk)

        # Do notices exist
        otc_notices = None
        # otc_notices = OpenToCollaborateNoticeURL.objects.filter(service_provider=service_provider)

        if request.user.is_authenticated:
            user_service_providers = (
                UserAffiliation.objects.prefetch_related("service_providers")
                .get(user=request.user)
                .service_providers.all()
            )
            form = ContactOrganizationForm(request.POST or None)

            if request.method == "POST":
                if "contact_btn" in request.POST:
                    # contact service provider
                    if form.is_valid():
                        from_name = form.cleaned_data["name"]
                        from_email = form.cleaned_data["email"]
                        message = form.cleaned_data["message"]
                        to_email = service_provider.account_creator.email

                        send_contact_email(
                            request,
                            to_email,
                            from_name,
                            from_email,
                            message,
                            service_provider,
                        )
                        messages.add_message(request, messages.SUCCESS, "Message sent!")
                        return redirect("public-service-provider", service_provider.id)
                    else:
                        if not form.data["message"]:
                            messages.add_message(
                                request,
                                messages.ERROR,
                                "Unable to send an empty message.",
                            )
                            return redirect("public-service-provider", service_provider.id)

                else:
                    messages.add_message(
                        request, messages.ERROR, "Something went wrong."
                    )
                    return redirect("public-service-provider", service_provider.id)

        else:
            context = {
                "service_provider": service_provider,
                "otc_notices": otc_notices,
                "env": environment,
            }
            return render(request, "public.html", context)

        context = {
            "service_provider": service_provider,
            "form": form,
            "user_service_providers": user_service_providers,
            "otc_notices": otc_notices,
            "env": environment,
        }
        return render(request, "public.html", context)
    except:
        raise Http404()
    
# Notices
@login_required(login_url="login")
# TODO: add is_researcher similar decorator
def service_provider_notices(request, pk):
    service_provider = get_service_provider(pk)
    # urls = OpenToCollaborateNoticeURL.objects.filter(
    #     service_provider=service_provider
    # ).values_list("url", "name", "id")
    # form = OpenToCollaborateNoticeURLForm(request.POST or None)
    # cc_policy_form = CollectionsCareNoticePolicyForm(
    #     request.POST or None, request.FILES
    # )
    # try:
    #     subscription = Subscription.objects.get(institution=institution)
    # except Subscription.DoesNotExist:
    #     subscription = None

    # sets permission to download OTC Notice
    if dev_prod_or_local(request.get_host()) == "SANDBOX":
        is_sandbox = True
        otc_download_perm = 0
        ccn_download_perm = 0
    else:
        is_sandbox = False
        otc_download_perm = 1 if service_provider.is_certified else 0
        ccn_download_perm = 1 if service_provider.is_certified else 0

    # if request.method == "POST":
    #     if "add_policy" in request.POST:
    #         pass
    #         if cc_policy_form.is_valid():
    #             cc_data = cc_policy_form.save(commit=False)
    #             cc_data.institution = institution
    #             cc_data.save()
    #     else:
    #         if form.is_valid():
    #             data = form.save(commit=False)
    #             data.institution = institution
    #             data.save()
    #             # Adds activity to Hub Activity
    #             HubActivity.objects.create(
    #                 action_user_id=request.user.id,
    #                 action_type="Engagement Notice Added",
    #                 project_id=data.id,
    #                 action_account_type="institution",
    #                 institution_id=institution.id,
    #             )
    #     return redirect("institution-notices", institution.id)

    context = {
        "service_provider": service_provider,
        # "form": form,
        # "cc_policy_form": cc_policy_form,
        # "urls": urls,
        "otc_download_perm": otc_download_perm,
        "ccn_download_perm": ccn_download_perm,
        "is_sandbox": is_sandbox,
    }
    return render(request, "serviceproviders/notices.html", context)