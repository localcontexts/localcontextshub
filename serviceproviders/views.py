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


# ACCOUNT CREATION
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


@login_required(login_url="login")
def confirm_subscription_service_provider(request, service_provider_id):
    join_flag = False
    service_provider = get_object_or_404(ServiceProvider, id=service_provider_id)
    initial_data = {
        "first_name": request.user._wrapped.first_name,
        "last_name": request.user._wrapped.last_name,
        "email": request.user._wrapped.email,
        "account_type": "service_provider_account",
        "organization_name": service_provider.name,
    }
    modified_inquiry_type_choices = [
        choice
        for choice in SubscriptionForm.INQUIRY_TYPE_CHOICES
        if choice[0] != "member"
    ]
    form = SubscriptionForm(request.POST or None, initial=initial_data)
    form.fields["inquiry_type"].choices = modified_inquiry_type_choices
    form.fields["account_type"].widget.attrs.update({"class": "w-100 readonly-input"})
    form.fields["organization_name"].widget.attrs.update({"class": "readonly-input"})
    form.fields["email"].widget.attrs.update({"class": "readonly-input"})
    if request.method == "POST":
        if validate_recaptcha(request) and form.is_valid():
            account_type_key = form.cleaned_data["account_type"]
            inquiry_type_key = form.cleaned_data["inquiry_type"]

            account_type_display = dict(form.fields["account_type"].choices).get(
                account_type_key, ""
            )
            inquiry_type_display = dict(form.fields["inquiry_type"].choices).get(
                inquiry_type_key, ""
            )
            form.cleaned_data["account_type"] = account_type_display
            form.cleaned_data["inquiry_type"] = inquiry_type_display

            first_name = form.cleaned_data["first_name"]
            if not form.cleaned_data["last_name"]:
                form.cleaned_data["last_name"] = first_name
            try:
                response = confirm_subscription(request, service_provider, join_flag, form)
                return response
            except:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "An unexpected error has occurred. Please contact support@localcontexts.org.",
                )
                return redirect("dashboard")
    return render(
        request,
        "accounts/confirm-subscription.html",
        {
            "form": form,
            "account": service_provider,
            "subscription_url": 'confirm-subscription-service-provider',
            "join_flag": join_flag,
        },
    )


def public_service_provider_view(request, pk):
    try:
        environment = dev_prod_or_local(request.get_host())
        service_provider = ServiceProvider.objects.get(id=pk)

        # Do notices exist
        otc_notices = OpenToCollaborateNoticeURL.objects.filter(service_provider=service_provider)

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
    urls = OpenToCollaborateNoticeURL.objects.filter(
        service_provider=service_provider
    ).values_list("url", "name", "id")
    form = OpenToCollaborateNoticeURLForm(request.POST or None)

    # sets permission to download OTC Notice
    if dev_prod_or_local(request.get_host()) == "SANDBOX":
        is_sandbox = True
        otc_download_perm = 0
        ccn_download_perm = 0
    else:
        is_sandbox = False
        otc_download_perm = 1 if service_provider.is_certified else 0
        ccn_download_perm = 1 if service_provider.is_certified else 0
    
    if request.method == "POST" and form.is_valid():
        data = form.save(commit=False)
        data.service_provider = service_provider
        data.save()
        # Adds activity to Hub Activity
        # HubActivity.objects.create(
        #     action_user_id=request.user.id,
        #     action_type="Engagement Notice Added",
        #     project_id=data.id,
        #     action_account_type="service_provider",
        #     service_provider_id=service_provider.id,
        # )
        return redirect("service-provider-notices", service_provider.id)

    context = {
        "service_provider": service_provider,
        "form": form,
        "urls": urls,
        "otc_download_perm": otc_download_perm,
        "ccn_download_perm": ccn_download_perm,
        "is_sandbox": is_sandbox,
    }
    return render(request, "serviceproviders/notices.html", context)

@login_required(login_url="login")
# TODO: add is_researcher similar decorator
def delete_otc_notice(request, pk, notice_id):
    if OpenToCollaborateNoticeURL.objects.filter(id=notice_id).exists():
        otc = OpenToCollaborateNoticeURL.objects.get(id=notice_id)
        otc.delete()
    return redirect("service-provider-notices", pk)

@login_required(login_url="login")
# TODO: add is_researcher similar decorator
def connections(request, pk):
    service_provider = get_service_provider(pk)

    context = {
        "service_provider": service_provider,
    }
    return render(request, "serviceproviders/connections.html", context)

# ACCOUNT SETTINGS
@login_required(login_url="login")
# TODO: add is_researcher similar decorator
def update_service_provider(request, pk):
    service_provider = get_service_provider(pk)

    if request.method == "POST":
        update_form = UpdateServiceProviderForm(
            request.POST, request.FILES, instance=service_provider
        )

        if "clear_image" in request.POST:
            service_provider.image = None
            service_provider.save()
            return redirect("update-service-provider", service_provider.id)
        else:
            if update_form.is_valid():
                update_form.save()
                messages.add_message(request, messages.SUCCESS, "Settings updated!")
                return redirect("update-service-provider", service_provider.id)
    else:
        update_form = UpdateServiceProviderForm(instance=service_provider)

    context = {
        "service_provider": service_provider,
        "update_form": update_form,
    }
    return render(request, 'account_settings_pages/_update-account.html', context)