from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from itertools import chain
from .decorators import member_required
from maintenance_mode.decorators import force_maintenance_mode_off

from localcontexts.utils import dev_prod_or_local
from helpers.utils import (
    InviteMember, validate_recaptcha, check_member_role, encrypt_api_key,
    form_initiation, change_member_role
)
from notifications.utils import (
    UserNotification, send_account_member_invite, send_simple_action_notification
)
from .utils import handle_service_provider_creation, get_service_provider

from django.contrib.auth.models import User
from helpers.models import OpenToCollaborateNoticeURL
from api.models import AccountAPIKey
from accounts.models import UserAffiliation, ServiceProviderConnections
from institutions.models import Institution
from communities.models import Community
from researchers.models import Researcher
from notifications.models import ActionNotification
from .models import ServiceProvider

from helpers.forms import OpenToCollaborateNoticeURLForm, HubActivity
from communities.forms import InviteMemberForm
from accounts.forms import ContactOrganizationForm, SignUpInvitationForm, SubscriptionForm
from api.forms import APIKeyGeneratorForm
from .forms import CreateServiceProviderForm, UpdateServiceProviderForm

from helpers.emails import send_contact_email, send_member_invite_email


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
    user_form = form_initiation(request)
    subscription_form = SubscriptionForm()
    env = dev_prod_or_local(request.get_host())

    if request.method == "POST":
        form = CreateServiceProviderForm(request.POST)
        if (form.is_valid() and user_form.is_valid() and validate_recaptcha(request)):
            mutable_post_data = request.POST.copy()
            subscription_data = {
                "first_name": user_form.cleaned_data['first_name'],
                "last_name": user_form.cleaned_data['last_name'],
                "email": request.user._wrapped.email,
                "inquiry_type": "Service Provider",
                "account_type": "service_provider_account",
                "organization_name": form.cleaned_data['name'],
            }

            mutable_post_data.update(subscription_data)
            subscription_form = SubscriptionForm(mutable_post_data)

            if subscription_form.is_valid():
                handle_service_provider_creation(request, form, subscription_form, env)
                return redirect('dashboard')
            else:
                messages.add_message(
                    request, messages.ERROR, "Something went wrong. Please Try again later."
                )
                return redirect('dashboard')

    context = {
        "form": form,
        "subscription_form": subscription_form,
        "user_form": user_form,
    }

    return render(request, "serviceproviders/create-service-provider.html", context)


# PUBLIC VIEW
def public_service_provider_view(request, pk):
    try:
        environment = dev_prod_or_local(request.get_host())
        service_provider = ServiceProvider.objects.get(id=pk)

        # Do notices exist
        otc_notices = OpenToCollaborateNoticeURL.objects.filter(
            service_provider=service_provider
        )

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
                            request, to_email, from_name, from_email, message, service_provider,
                        )
                        messages.add_message(request, messages.SUCCESS, "Message sent!")
                        return redirect("public-service-provider", service_provider.id)
                    else:
                        if not form.data["message"]:
                            messages.add_message(
                                request, messages.ERROR, "Unable to send an empty message.",
                            )
                            return redirect("public-service-provider", service_provider.id)

                else:
                    messages.add_message(request, messages.ERROR, "Something went wrong.")
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


# NOTICES
@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def service_provider_notices(request, pk):
    service_provider = get_service_provider(pk)
    member_role = check_member_role(request.user, service_provider)
    urls = OpenToCollaborateNoticeURL.objects.filter(service_provider=service_provider
                                                            ).values_list("url", "name", "id")
    form = OpenToCollaborateNoticeURLForm(request.POST or None)

    if service_provider.is_certified:
        not_approved_download_notice = None
        not_approved_shared_notice = None
    else:
        not_approved_download_notice = "Your service provider account needs to be subscribed " \
            "in order to download this Notice."
        not_approved_shared_notice = "Your service provider account needs to be subscribed in " \
            "order to share this Notice."

    # sets permission to download OTC Notice
    if dev_prod_or_local(request.get_host()) == "SANDBOX":
        is_sandbox = True
        otc_download_perm = 0
        download_notice_on_sandbox = "Download of Notices is not available on the sandbox site."
        share_notice_on_sandbox = "Sharing of Notices is not available on the sandbox site."
    else:
        is_sandbox = False
        otc_download_perm = 1 if service_provider.is_certified else 0
        download_notice_on_sandbox = None
        share_notice_on_sandbox = None

    if request.method == "POST" and form.is_valid():
        data = form.save(commit=False)
        data.service_provider = service_provider
        data.save()
        # Adds activity to Hub Activity
        HubActivity.objects.create(
            action_user_id=request.user.id,
            action_type="Engagement Notice Added",
            project_id=data.id,
            action_account_type="service_provider",
            service_provider_id=service_provider.id,
        )
        return redirect("service-provider-notices", service_provider.id)

    context = {
        "service_provider": service_provider,
        "member_role": member_role,
        "form": form,
        "urls": urls,
        "otc_download_perm": otc_download_perm,
        'not_approved_download_notice': not_approved_download_notice,
        'download_notice_on_sandbox': download_notice_on_sandbox,
        'not_approved_shared_notice': not_approved_shared_notice,
        'share_notice_on_sandbox': share_notice_on_sandbox,
        "is_sandbox": is_sandbox,
    }
    return render(request, "serviceproviders/notices.html", context)


@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def delete_otc_notice(request, pk, notice_id):
    if OpenToCollaborateNoticeURL.objects.filter(id=notice_id).exists():
        otc = OpenToCollaborateNoticeURL.objects.get(id=notice_id)
        otc.delete()
    return redirect("service-provider-notices", pk)


@force_maintenance_mode_off
def embed_otc_notice(request, pk):
    layout = request.GET.get("lt")
    lang = request.GET.get("lang")
    align = request.GET.get("align")

    service_provider = get_service_provider(pk)
    otc_notices = OpenToCollaborateNoticeURL.objects.filter(service_provider=service_provider)

    context = {
        "layout": layout,
        "lang": lang,
        "align": align,
        "otc_notices": otc_notices,
        "service_provider": service_provider,
    }

    response = render(request, "partials/_embed.html", context)
    response["Content-Security-Policy"] = "frame-ancestors https://*"

    return response


# CONNECTIONS
@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def connections(request, pk):
    try:
        service_provider = get_service_provider(pk)
        member_role = check_member_role(request.user, service_provider)
        if request.method == "GET":
            sp_connections = ServiceProviderConnections.objects.filter(
                service_provider=service_provider
            )

            institution_ids = sp_connections.values_list('institutions__id', flat=True)
            community_ids = sp_connections.values_list('communities__id', flat=True)
            researcher_ids = sp_connections.values_list('researchers__id', flat=True)

            communities = Community.objects.filter(id__in=community_ids)
            researchers = Researcher.objects.filter(id__in=researcher_ids)
            institutions = Institution.objects.filter(id__in=institution_ids)

        elif request.method == "POST":
            if "disconnectAccount" in request.POST:
                connection_reference_id = f"{service_provider.id}:{request.POST.get('disconnectAccount')}"
                account_id, account_type = request.POST.get('disconnectAccount').split('_')
                sp_connection = ServiceProviderConnections.objects.get(
                    service_provider=service_provider
                )

                # Delete instances of the connection notification
                if ActionNotification.objects.filter(
                    reference_id=connection_reference_id
                ).exists():
                    for notification in ActionNotification.objects.filter(
                        reference_id=connection_reference_id
                    ):
                        notification.delete()

                if account_type == "i":
                    sp_connection.institutions.remove(account_id)

                    # Send notification of disconnection to account
                    institution = Institution.objects.get(id=account_id)
                    title = f"{service_provider.name} (Service Provider) has removed your "\
                        "connection"
                    send_simple_action_notification(
                        None, institution, title, "Activity", connection_reference_id
                    )


                elif account_type == "c":
                    sp_connection.communities.remove(account_id)

                    # Send notification of disconnection to account
                    community = Community.objects.get(id=account_id)
                    title = f"{service_provider.name} (Service Provider) has removed your "\
                        "connection"
                    send_simple_action_notification(
                        None, community, title, "Activity", connection_reference_id
                    )

                elif account_type == "r":
                    sp_connection.researchers.remove(account_id)
                    # name = get_users_name(request.user)

                    # Send notification of disconnection to account
                    researcher = Researcher.objects.get(id=account_id)
                    title = f"{service_provider.name} (Service Provider) has removed your "\
                        "connection"
                    send_simple_action_notification(
                        None, researcher, title, "Activity", connection_reference_id
                    )

                sp_connection.save()

            return redirect("service-provider-connections", service_provider.id)

        context = {
            "service_provider": service_provider,
            "member_role": member_role,
            "communities": communities,
            "researchers": researchers,
            "institutions": institutions,
        }
        return render(request, "serviceproviders/connections.html", context)

    except:
        raise Http404()


# MEMBERS
@login_required(login_url='login')
@member_required(roles=['admin', 'editor'])
def service_provider_members(request, pk):
    service_provider = get_service_provider(pk)
    member_role = check_member_role(request.user, service_provider)

    # Get list of users, NOT in this account, alphabetized by name
    members = list(chain(
        service_provider.editors.all().values_list('id', flat=True),
    ))

    # include account creator
    members.append(service_provider.account_creator.id)
    users = User.objects.exclude(id__in=members).order_by('username')

    form = InviteMemberForm(request.POST or None, service_provider=service_provider)

    if request.method == "POST":
        if 'change_member_role_btn' in request.POST:
            current_role = request.POST.get('current_role')
            new_role = request.POST.get('new_role')
            user_id = request.POST.get('user_id')
            member = User.objects.get(id=user_id)
            change_member_role(service_provider, member, current_role, new_role)
            return redirect('members', service_provider.id)

        elif 'send_invite_btn' in request.POST:
            selected_user = User.objects.none()
            if form.is_valid():
                data = form.save(commit=False)

                # Get target User
                selected_username = request.POST.get('userList')
                username_to_check = ''

                '''if username includes spaces means it has a
                first and last name (last name,first name)'''
                if ' ' in selected_username:
                    x = selected_username.split(' ')
                    username_to_check = x[0]
                else:
                    username_to_check = selected_username

                if not username_to_check in users.values_list(
                    'username', flat=True
                ):
                    message = "Invalid user selection. Please select user from the list."
                    messages.add_message(request, messages.INFO, message)
                else:
                    selected_user = User.objects.get(username=username_to_check)

                    # Check to see if an invite request aleady exists
                    invitation_exists = InviteMember.objects.filter(
                        receiver=selected_user,
                        service_provider=service_provider
                    ).exists() # Check to see if invitation already exists

                    # If invitation request does not exist, save form
                    if not invitation_exists:
                        data.receiver = selected_user
                        data.sender = request.user
                        data.status = 'sent'
                        data.service_provider = service_provider
                        data.save()

                        # Send action notification
                        send_account_member_invite(data)

                        # Send email to target user
                        send_member_invite_email(request, data, service_provider)
                        messages.add_message(
                            request, messages.INFO, f'Invitation sent to {selected_user}!'
                        )
                        return redirect('service-provider-members', service_provider.id)
                    else:
                        message = f"The user you are trying to add already has an invitation" \
                            f"invitation pending to join {service_provider.name}."
                        messages.add_message(request, messages.INFO, message)
            else:
                messages.add_message(request, messages.INFO, 'Something went wrong.')

    context = {
        'service_provider': service_provider,
        'member_role': member_role,
        'form': form,
        'users': users,
        'invite_form': SignUpInvitationForm(),
        'env': dev_prod_or_local(request.get_host()),
    }
    return render(request, 'serviceproviders/members.html', context)


@login_required(login_url='login')
@member_required(roles=['admin', 'editor', 'viewer'])
def service_provider_member_invites(request, pk):
    service_provider = get_service_provider(pk)
    member_role = check_member_role(request.user, service_provider)
    member_invites = InviteMember.objects.filter(service_provider=service_provider)

    context = {
        'member_role': member_role,
        'service_provider': service_provider,
        'member_invites': member_invites,
    }
    return render(request, 'serviceproviders/member-requests.html', context)


@login_required(login_url='login')
@member_required(roles=['admin'])
def service_provider_remove_member(request, pk, member_id):
    service_provider = get_service_provider(pk)
    member = User.objects.get(id=member_id)
    # what role does member have
    # remove from role
    if member in service_provider.editors.all():
        service_provider.editors.remove(member)

    # remove account from userAffiliation instance
    affiliation = UserAffiliation.objects.get(user=member)
    affiliation.service_providers.remove(service_provider)

    title = f'You have been removed as a member from {service_provider.name}.'
    UserNotification.objects.create(
        from_user=request.user,
        to_user=member,
        title=title,
        notification_type="Remove",
        service_provider=service_provider
    )

    if '/manage/' in request.META.get('HTTP_REFERER'):
        return redirect('manage-orgs')
    else:
        return redirect('service-provider-members', service_provider.id)


# ACCOUNT SETTINGS
@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def update_service_provider(request, pk):
    service_provider = get_service_provider(pk)
    member_role = check_member_role(request.user, service_provider)

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
        "member_role": member_role,
    }
    return render(
        request, 'account_settings_pages/_update-account.html', context
    )


@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def api_keys(request, pk):
    service_provider = get_service_provider(pk)
    member_role = check_member_role(request.user, service_provider)
    remaining_api_key_count = 0

    try:
        account_keys = AccountAPIKey.objects.filter(
            service_provider=service_provider
        ).values_list("prefix", "name", "encrypted_key")

        if service_provider.is_certified and account_keys.count() == 0:
            remaining_api_key_count = 1

        if request.method == 'GET':
            form = APIKeyGeneratorForm(request.GET or None)

        elif request.method == "POST":
            if "generate_api_key" in request.POST:
                if (service_provider.is_certified and
                    remaining_api_key_count == 0):
                    messages.add_message(
                        request,
                        messages.ERROR,
                        'Your account has reached its API Key limit.'
                    )
                    return redirect(
                        "service-provider-api-key", service_provider.id
                    )
                form = APIKeyGeneratorForm(request.POST)

                if service_provider.is_certified and form.is_valid():
                    data = form.save(commit=False)
                    api_key, key = AccountAPIKey.objects.create_key(
                        name = data.name,
                        service_provider_id = service_provider.id
                    )
                    prefix = key.split(".")[0]
                    encrypted_key = encrypt_api_key(key)
                    AccountAPIKey.objects.filter(
                        prefix=prefix).update(encrypted_key=encrypted_key)

                else:
                    message = "Your account is not confirmed. Your " \
                        "account must be confirmed to create an API Key."
                    messages.add_message(
                        request,
                        messages.ERROR,
                        message
                    )
                    return redirect(
                        "service-provider-api-key", service_provider.id
                    )

                return redirect(
                    "service-provider-api-key", service_provider.id
                )

            elif "delete_api_key" in request.POST:
                prefix = request.POST['delete_api_key']
                api_key = AccountAPIKey.objects.filter(prefix=prefix)
                api_key.delete()

                return redirect(
                    "service-provider-api-key", service_provider.id
                )

        context = {
            "service_provider" : service_provider,
            "form" : form,
            "account_keys" : account_keys,
            "member_role" : member_role,
            "remaining_api_key_count" : remaining_api_key_count,
        }
        return render(
            request, 'account_settings_pages/_api-keys.html', context
        )
    except:
        raise Http404()
