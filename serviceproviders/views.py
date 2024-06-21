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
        # if noror_form.is_valid() and user_form.is_valid() and validate_recaptcha(request):
        if form.is_valid() and validate_recaptcha(request):
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
                handle_service_provider_creation(request, form, subscription_form )
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