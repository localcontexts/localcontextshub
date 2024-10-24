from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.db.models import Q
from itertools import chain
from .decorators import member_required
from django.shortcuts import get_object_or_404

from localcontexts.utils import dev_prod_or_local
from projects.utils import *
from helpers.utils import *
from notifications.utils import *
from .utils import *
from accounts.utils import remove_user_from_account

from .models import *
from projects.models import *
from communities.models import Community, JoinRequest
from notifications.models import ActionNotification
from helpers.models import *
from api.models import AccountAPIKey

from django.contrib.auth.models import User
from accounts.models import UserAffiliation, Subscription, ServiceProviderConnections

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
)
from api.forms import APIKeyGeneratorForm
from .forms import *

from helpers.emails import *
from maintenance_mode.decorators import force_maintenance_mode_off
from django.db import transaction


@login_required(login_url="login")
def connect_institution(request):
    institution = True
    institutions = Institution.subscribed.all()
    form = JoinRequestForm(request.POST or None)

    if request.method == "POST":
        institution_name = request.POST.get("organization_name")
        if Institution.objects.filter(institution_name=institution_name).exists():
            institution = Institution.objects.get(institution_name=institution_name)

            # If join request exists or user is already a member, display Error message
            request_exists = JoinRequest.objects.filter(
                user_from=request.user, institution=institution
            ).exists()
            user_is_member = institution.is_user_in_institution(request.user)

            if request_exists or user_is_member:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Either you have already sent this request or are currently a member of this institution.",
                )
                return redirect("connect-institution")
            else:
                if form.is_valid():
                    data = form.save(commit=False)
                    data.user_from = request.user
                    data.institution = institution
                    data.user_to = institution.institution_creator
                    data.save()

                    send_action_notification_join_request(
                        data
                    )  # Send action notification to institution
                    send_join_request_email_admin(
                        request, data, institution
                    )  # Send institution creator email
                    messages.add_message(
                        request, messages.SUCCESS, "Request to join institution sent!"
                    )
                    return redirect("connect-institution")
        else:
            messages.add_message(
                request, messages.ERROR, "Institution not in registry."
            )
            return redirect("connect-institution")

    context = {
        "institution": institution,
        "institutions": institutions,
        "form": form,
    }
    return render(request, "institutions/connect-institution.html", context)


@login_required(login_url="login")
def preparation_step(request):
    if dev_prod_or_local(request.get_host()) == "SANDBOX":
        return redirect("create-institution")
    else:
        institution = True
        return render(
            request, "accounts/preparation.html", {"institution": institution}
        )


@login_required(login_url="login")
def create_institution(request):
    form = CreateInstitutionForm()
    user_form = form_initiation(request)
    env = dev_prod_or_local(request.get_host())
    
    if request.method == "POST":
        form = CreateInstitutionForm(request.POST)
        if form.is_valid() and user_form.is_valid() and validate_recaptcha(request):
            mutable_post_data = request.POST.copy()
            subscription_data = {
                "first_name": user_form.cleaned_data['first_name'],
                "last_name": user_form.cleaned_data['last_name'],
                "email": request.user._wrapped.email,
                "account_type": "institution_account",
                "inquiry_type": request.POST['inquiry_type'],
                "organization_name": form.cleaned_data['institution_name'],
            }
            
            mutable_post_data.update(subscription_data)
            subscription_form = SubscriptionForm(mutable_post_data)

            if subscription_form.is_valid():
                handle_institution_creation(request, form, subscription_form, env )
                return redirect('dashboard')
            else:
                messages.add_message(
                    request, messages.ERROR, "Something went wrong. Please Try again later.",
                )
                return redirect('dashboard')
    return render(
        request, "institutions/create-institution.html", {
            "form": form, "user_form": user_form,
        }
    )


@login_required(login_url="login")
def create_custom_institution(request):
    noror_form = CreateInstitutionNoRorForm()
    user_form = form_initiation(request)
    env = dev_prod_or_local(request.get_host())

    if request.method == "POST":
        noror_form = CreateInstitutionNoRorForm(request.POST)
        if noror_form.is_valid() and user_form.is_valid() and validate_recaptcha(request):
            mutable_post_data = request.POST.copy()
            subscription_data = {
            "first_name": user_form.cleaned_data['first_name'],
            "last_name": user_form.cleaned_data['last_name'],
            "email": request.user._wrapped.email,
            "account_type": "institution_account",
            "inquiry_type": request.POST['inquiry_type'],
            "organization_name": noror_form.cleaned_data['institution_name'],
            }
            
            mutable_post_data.update(subscription_data)
            subscription_form = SubscriptionForm(mutable_post_data)
            if subscription_form.is_valid():
                handle_institution_creation(request, noror_form, subscription_form, env )
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
        "institutions/create-custom-institution.html",
        {
            "noror_form": noror_form,
            "user_form": user_form,
        },
    )


def public_institution_view(request, pk):
    try:
        environment = dev_prod_or_local(request.get_host())
        institution = Institution.objects.get(id=pk)

        # Do notices exist
        bcnotice = Notice.objects.filter(
            institution=institution, notice_type="biocultural"
        ).exists()
        tknotice = Notice.objects.filter(
            institution=institution, notice_type="traditional_knowledge"
        ).exists()
        attrnotice = Notice.objects.filter(
            institution=institution, notice_type="attribution_incomplete"
        ).exists()
        otc_notices = OpenToCollaborateNoticeURL.objects.filter(institution=institution)

        projects_list = list(
            chain(
                institution.institution_created_project.all().values_list(
                    "project__unique_id", flat=True
                ),  # institution created project ids
                institution.contributing_institutions.all().values_list(
                    "project__unique_id", flat=True
                ),  # projects where institution is contributor
            )
        )
        project_ids = list(set(projects_list))  # remove duplicate ids
        archived = ProjectArchived.objects.filter(
            project_uuid__in=project_ids, institution_id=institution.id, archived=True
        ).values_list(
            "project_uuid", flat=True
        )  # check ids to see if they are archived
        projects = (
            Project.objects.select_related("project_creator")
            .filter(unique_id__in=project_ids, project_privacy="Public")
            .exclude(unique_id__in=archived)
            .order_by("-date_modified")
        )

        if request.user.is_authenticated:
            user_institutions = (
                UserAffiliation.objects.prefetch_related("institutions")
                .get(user=request.user)
                .institutions.all()
            )
            form = ContactOrganizationForm(request.POST or None)
            join_form = JoinRequestForm(request.POST or None)

            if request.method == "POST":
                if "contact_btn" in request.POST:
                    # contact institution
                    if form.is_valid():
                        from_name = form.cleaned_data["name"]
                        from_email = form.cleaned_data["email"]
                        message = form.cleaned_data["message"]
                        to_email = institution.institution_creator.email

                        send_contact_email(
                            request,
                            to_email,
                            from_name,
                            from_email,
                            message,
                            institution,
                        )
                        messages.add_message(request, messages.SUCCESS, "Message sent!")
                        return redirect("public-institution", institution.id)
                    else:
                        if not form.data["message"]:
                            messages.add_message(
                                request,
                                messages.ERROR,
                                "Unable to send an empty message.",
                            )
                            return redirect("public-institution", institution.id)

                elif "join_request" in request.POST:
                    if join_form.is_valid():
                        data = join_form.save(commit=False)
                        if JoinRequest.objects.filter(
                            user_from=request.user, institution=institution
                        ).exists():
                            messages.add_message(
                                request,
                                messages.ERROR,
                                "You have already sent a request to this institution.",
                            )
                            return redirect("public-institution", institution.id)
                        else:
                            data.user_from = request.user
                            data.institution = institution
                            data.user_to = institution.institution_creator
                            data.save()

                            send_action_notification_join_request(
                                data
                            )  # Send action notification to institution
                            send_join_request_email_admin(
                                request, data, institution
                            )  # Send email to institution creator
                            return redirect("public-institution", institution.id)
                else:
                    messages.add_message(
                        request, messages.ERROR, "Something went wrong."
                    )
                    return redirect("public-institution", institution.id)

        else:
            context = {
                "institution": institution,
                "projects": projects,
                "bcnotice": bcnotice,
                "tknotice": tknotice,
                "attrnotice": attrnotice,
                "otc_notices": otc_notices,
                "env": environment,
            }
            return render(request, "public.html", context)

        context = {
            "institution": institution,
            "projects": projects,
            "form": form,
            "join_form": join_form,
            "user_institutions": user_institutions,
            "bcnotice": bcnotice,
            "tknotice": tknotice,
            "attrnotice": attrnotice,
            "otc_notices": otc_notices,
            "env": environment,
        }
        return render(request, "public.html", context)
    except:
        raise Http404()


# Update institution
@login_required(login_url="login")
@member_required(roles=["admin", "editor", "viewer"])
def update_institution(request, pk):
    institution = get_institution(pk)
    member_role = check_member_role(request.user, institution)
    envi = dev_prod_or_local(request.get_host())

    if request.method == "POST":
        update_form = UpdateInstitutionForm(
            request.POST, request.FILES, instance=institution
        )

        if "clear_image" in request.POST:
            institution.image = None
            institution.save()
            return redirect("update-institution", institution.id)
        else:
            if update_form.is_valid():
                update_form.save()
                messages.add_message(request, messages.SUCCESS, "Settings updated!")
                return redirect("update-institution", institution.id)
    else:
        update_form = UpdateInstitutionForm(instance=institution)

    context = {
        "institution": institution,
        "update_form": update_form,
        "member_role": member_role,
        "envi": envi,
    }
    return render(request, 'account_settings_pages/_update-account.html', context)


# Notices
@login_required(login_url="login")
@member_required(roles=["admin", "editor", "viewer"])
def institution_notices(request, pk):
    institution = get_institution(pk)
    member_role = check_member_role(request.user, institution)
    urls = OpenToCollaborateNoticeURL.objects.filter(
        institution=institution
    ).values_list("url", "name", "id")
    form = OpenToCollaborateNoticeURLForm(request.POST or None)
    cc_policy_form = CollectionsCareNoticePolicyForm(
        request.POST or None, request.FILES
    )

    try:
        subscription = Subscription.objects.get(institution=institution)
        not_approved_download_notice = None
        not_approved_shared_notice = None
    except Subscription.DoesNotExist:
        subscription = None
        not_approved_download_notice = "Your institution account needs to be subscribed in order to download this Notice."
        not_approved_shared_notice = "Your institution account needs to be subscribed in order to share this Notice."

    # sets permission to download OTC Notice
    if dev_prod_or_local(request.get_host()) == "SANDBOX":
        is_sandbox = True
        otc_download_perm = 0
        ccn_download_perm = 0
        download_notice_on_sandbox = "Download of Notices is not available on the sandbox site."
        share_notice_on_sandbox = "Sharing of Notices is not available on the sandbox site."
    else:
        is_sandbox = False
        otc_download_perm = 1 if institution.is_subscribed else 0
        ccn_download_perm = 1 if institution.is_subscribed else 0
        download_notice_on_sandbox = None
        share_notice_on_sandbox = None

    if request.method == "POST":
        if "add_policy" in request.POST:
            if cc_policy_form.is_valid():
                cc_data = cc_policy_form.save(commit=False)
                cc_data.institution = institution
                cc_data.save()
        else:
            if form.is_valid():
                data = form.save(commit=False)
                data.institution = institution
                data.save()
                # Adds activity to Hub Activity
                HubActivity.objects.create(
                    action_user_id=request.user.id,
                    action_type="Engagement Notice Added",
                    project_id=data.id,
                    action_account_type="institution",
                    institution_id=institution.id,
                )
        return redirect("institution-notices", institution.id)

    context = {
        "institution": institution,
        "member_role": member_role,
        "form": form,
        "cc_policy_form": cc_policy_form,
        "urls": urls,
        "otc_download_perm": otc_download_perm,
        "ccn_download_perm": ccn_download_perm,
        "is_sandbox": is_sandbox,
        'not_approved_download_notice': not_approved_download_notice,
        'download_notice_on_sandbox': download_notice_on_sandbox,
        'not_approved_shared_notice': not_approved_shared_notice,
        'share_notice_on_sandbox': share_notice_on_sandbox,
        "subscription": subscription,
    }
    return render(request, "institutions/notices.html", context)


@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def delete_otc_notice(request, pk, notice_id):
    if OpenToCollaborateNoticeURL.objects.filter(id=notice_id).exists():
        otc = OpenToCollaborateNoticeURL.objects.get(id=notice_id)
        otc.delete()
    return redirect("institution-notices", pk)


# Members
@login_required(login_url="login")
@member_required(roles=["admin", "editor", "viewer"])
def institution_members(request, pk):
    institution = get_institution(pk)
    member_role = check_member_role(request.user, institution)
    # Get list of users, NOT in this institution, alphabetized by name
    members = list(
        chain(
            institution.admins.all().values_list("id", flat=True),
            institution.editors.all().values_list("id", flat=True),
            institution.viewers.all().values_list("id", flat=True),
        )
    )
    members.append(institution.institution_creator.id)  # include institution creator
    users = User.objects.exclude(id__in=members).order_by("username")

    join_requests_count = JoinRequest.objects.filter(institution=institution).count()
    try:
        subscription = Subscription.objects.get(institution=institution)
    except Subscription.DoesNotExist:
        subscription = None
    form = InviteMemberForm(request.POST or None, subscription=subscription)

    if request.method == "POST":
        if "change_member_role_btn" in request.POST:
            current_role = request.POST.get("current_role")
            new_role = request.POST.get("new_role")
            user_id = request.POST.get("user_id")
            member = User.objects.get(id=user_id)
            check_subscription_and_then_change_role(request, institution, member, current_role, new_role)
            return redirect("institution-members", institution.id)

        elif "send_invite_btn" in request.POST:
            selected_user = User.objects.none()
            if form.is_valid():
                data = form.save(commit=False)

                # Get target User
                selected_username = request.POST.get("userList")
                username_to_check = ""

                if (
                    " " in selected_username
                ):  # if username includes spaces means it has a first and last name (last name,first name)
                    x = selected_username.split(" ")
                    username_to_check = x[0]
                else:
                    username_to_check = selected_username

                if not username_to_check in users.values_list("username", flat=True):
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Invalid user selection. Please select user from the list.",
                    )
                else:
                    selected_user = User.objects.get(username=username_to_check)

                    # Check to see if an invite or join request aleady exists
                    invitation_exists = InviteMember.objects.filter(
                        receiver=selected_user, institution=institution
                    ).exists()  # Check to see if invitation already exists
                    join_request_exists = JoinRequest.objects.filter(
                        user_from=selected_user, institution=institution
                    ).exists()  # Check to see if join request already exists
                    if request.POST.get('role') in ('editor', 'administrator', 'admin') and subscription == None:
                        messages.error(request, 'The subscription process of your institution is not completed yet. Please wait for the completion of subscription process.')
                        return redirect('institution-members', institution.id)
                    elif request.POST.get('role') in ('editor', 'administrator', 'admin') and subscription.users_count == 0:
                        messages.error(request, 'The editor and admin limit for this institution has been reached. Please contact the institution and let them know to upgrade their subscription plan to add more editors and admins.')
                        return redirect('institution-members', institution.id)
                    
                    if (
                        not invitation_exists and not join_request_exists
                    ):  # If invitation and join request does not exist, save form
                        data.receiver = selected_user
                        data.sender = request.user
                        data.status = "sent"
                        data.institution = institution
                        data.save()

                        send_account_member_invite(data)  # Send action notification
                        send_member_invite_email(
                            request, data, institution
                        )  # Send email to target user
                        messages.add_message(
                            request,
                            messages.INFO,
                            f"Invitation sent to {selected_user}.",
                        )
                        return redirect("institution-members", institution.id)
                    else:
                        messages.add_message(
                            request,
                            messages.INFO,
                            f"The user you are trying to add already has an invitation pending to join {institution.institution_name}.",
                        )
            else:
                messages.add_message(request, messages.INFO, "Something went wrong.")

    context = {
        "institution": institution,
        "form": form,
        "member_role": member_role,
        "join_requests_count": join_requests_count,
        "users": users,
        "invite_form": SignUpInvitationForm(),
        "env": dev_prod_or_local(request.get_host()),
        "subscription": subscription,
    }
    return render(request, "institutions/members.html", context)


@login_required(login_url="login")
@member_required(roles=["admin", "editor", "viewer"])
def member_requests(request, pk):
    institution = get_institution(pk)
    member_role = check_member_role(request.user, institution)
    join_requests = JoinRequest.objects.filter(institution=institution)
    member_invites = InviteMember.objects.filter(institution=institution)
    try:
        subscription = Subscription.objects.get(institution=institution)
    except Subscription.DoesNotExist:
        subscription = None
    
    if request.method == 'POST':
        selected_role = request.POST.get('selected_role')
        join_request_id = request.POST.get('join_request_id')
        if check_subscription(request, institution) and selected_role.lower() in ('editor', 'administrator', 'admin'):
            messages.add_message(request, messages.ERROR, 'The subscription process of your institution is not completed yet. Please wait for the completion of subscription process.')
            return redirect('institution-members', institution.id)
        
        accepted_join_request(request, institution, join_request_id, selected_role)
        return redirect('institution-member-requests', institution.id)

    context = {
        "member_role": member_role,
        "institution": institution,
        "join_requests": join_requests,
        "member_invites": member_invites,
        "subscription": subscription,
    }
    return render(request, "institutions/member-requests.html", context)


@login_required(login_url="login")
@member_required(roles=["admin"])
def delete_join_request(request, pk, join_id):
    institution = get_institution(pk)
    join_request = JoinRequest.objects.get(id=join_id)
    join_request.delete()
    return redirect('institution-member-requests', institution.id)

@login_required(login_url='login')
@member_required(roles=['admin'])
def remove_member(request, pk, member_id):
    institution = get_institution(pk)
    member = User.objects.get(id=member_id)
    try:
        subscription = Subscription.objects.get(institution=institution)
    except Subscription.DoesNotExist:
        subscription = None


    if subscription is not None and subscription.users_count >= 0 and member in (institution.admins.all() or institution.editors.all()):
        subscription.users_count += 1
        subscription.save()
    
    remove_user_from_account(member, institution)

    # Delete join request for this institution if exists
    if JoinRequest.objects.filter(user_from=member, institution=institution).exists():
        join_request = JoinRequest.objects.get(
            user_from=member, institution=institution
        )
        join_request.delete()

    title = f"You have been removed as a member from {institution.institution_name}."
    UserNotification.objects.create(
        from_user=request.user,
        to_user=member,
        title=title,
        notification_type="Remove",
        institution=institution,
    )

    if "/manage/" in request.META.get("HTTP_REFERER"):
        return redirect("manage-orgs")
    else:
        return redirect("institution-members", institution.id)


# Projects page
@login_required(login_url='login')
@member_required(roles=['admin', 'editor', 'viewer'])
def institution_projects(request, pk):
    institution = get_institution(pk)
    member_role = check_member_role(request.user, institution)
    try:
        subscription = Subscription.objects.get(institution=institution)
    except Subscription.DoesNotExist:
        subscription = None
    bool_dict = {
        "has_labels": False,
        "has_notices": False,
        "created": False,
        "contributed": False,
        "is_archived": False,
        "title_az": False,
        "visibility_public": False,
        "visibility_contributor": False,
        "visibility_private": False,
        "date_modified": False,
    }

    # 1. institution projects +
    # 2. projects institution has been notified of
    # 3. projects where institution is contributor

    projects_list = list(
        chain(
            institution.institution_created_project.all().values_list(
                "project__unique_id", flat=True
            ),
            institution.institutions_notified.all().values_list(
                "project__unique_id", flat=True
            ),
            institution.contributing_institutions.all().values_list(
                "project__unique_id", flat=True
            ),
        )
    )
    project_ids = list(set(projects_list))  # remove duplicate ids
    archived = ProjectArchived.objects.filter(
        project_uuid__in=project_ids, institution_id=institution.id, archived=True
    ).values_list(
        "project_uuid", flat=True
    )  # check ids to see if they are archived
    projects = (
        Project.objects.select_related("project_creator")
        .prefetch_related("bc_labels", "tk_labels")
        .filter(unique_id__in=project_ids)
        .exclude(unique_id__in=archived)
        .order_by("-date_added")
    )

    sort_by = request.GET.get("sort")
    if sort_by == "all":
        return redirect("institution-projects", institution.id)

    elif sort_by == "has_labels":
        projects = Project.objects.select_related("project_creator").prefetch_related(
            "bc_labels", "tk_labels"
        ).filter(unique_id__in=project_ids).exclude(unique_id__in=archived).exclude(
            bc_labels=None
        ).order_by(
            "-date_added"
        ) | Project.objects.select_related(
            "project_creator"
        ).prefetch_related(
            "bc_labels", "tk_labels"
        ).filter(
            unique_id__in=project_ids
        ).exclude(
            unique_id__in=archived
        ).exclude(
            tk_labels=None
        ).order_by(
            "-date_added"
        )
        bool_dict["has_labels"] = True

    elif sort_by == "has_notices":
        projects = (
            Project.objects.select_related("project_creator")
            .prefetch_related("bc_labels", "tk_labels")
            .filter(unique_id__in=project_ids, tk_labels=None, bc_labels=None)
            .exclude(unique_id__in=archived)
            .order_by("-date_added")
        )
        bool_dict["has_notices"] = True

    elif sort_by == "created":
        created_projects = institution.institution_created_project.all().values_list(
            "project__unique_id", flat=True
        )
        archived = ProjectArchived.objects.filter(
            project_uuid__in=created_projects,
            institution_id=institution.id,
            archived=True,
        ).values_list(
            "project_uuid", flat=True
        )  # check ids to see if they are archived
        projects = (
            Project.objects.select_related("project_creator")
            .prefetch_related("bc_labels", "tk_labels")
            .filter(unique_id__in=created_projects)
            .exclude(unique_id__in=archived)
            .order_by("-date_added")
        )
        bool_dict["created"] = True

    elif sort_by == "contributed":
        contrib = institution.contributing_institutions.all().values_list(
            "project__unique_id", flat=True
        )
        projects_list = list(
            chain(
                institution.institution_created_project.all().values_list(
                    "project__unique_id", flat=True
                ),  # check institution created projects
                ProjectArchived.objects.filter(
                    project_uuid__in=contrib,
                    institution_id=institution.id,
                    archived=True,
                ).values_list(
                    "project_uuid", flat=True
                ),  # check ids to see if they are archived
            )
        )
        project_ids = list(set(projects_list))  # remove duplicate ids
        projects = (
            Project.objects.select_related("project_creator")
            .prefetch_related("bc_labels", "tk_labels")
            .filter(unique_id__in=contrib)
            .exclude(unique_id__in=project_ids)
            .order_by("-date_added")
        )
        bool_dict["contributed"] = True

    elif sort_by == "archived":
        archived_projects = ProjectArchived.objects.filter(
            institution_id=institution.id, archived=True
        ).values_list("project_uuid", flat=True)
        projects = (
            Project.objects.select_related("project_creator")
            .prefetch_related("bc_labels", "tk_labels")
            .filter(unique_id__in=archived_projects)
            .order_by("-date_added")
        )
        bool_dict["is_archived"] = True

    elif sort_by == "title_az":
        projects = projects.order_by("title")
        bool_dict["title_az"] = True

    elif sort_by == "visibility_public":
        projects = (
            Project.objects.select_related("project_creator")
            .prefetch_related("bc_labels", "tk_labels")
            .filter(unique_id__in=project_ids, project_privacy="Public")
            .exclude(unique_id__in=archived)
            .order_by("-date_added")
        )
        bool_dict["visibility_public"] = True

    elif sort_by == "visibility_contributor":
        projects = (
            Project.objects.select_related("project_creator")
            .prefetch_related("bc_labels", "tk_labels")
            .filter(unique_id__in=project_ids, project_privacy="Contributor")
            .exclude(unique_id__in=archived)
            .order_by("-date_added")
        )
        bool_dict["visibility_contributor"] = True

    elif sort_by == "visibility_private":
        projects = (
            Project.objects.select_related("project_creator")
            .prefetch_related("bc_labels", "tk_labels")
            .filter(unique_id__in=project_ids, project_privacy="Private")
            .exclude(unique_id__in=archived)
            .order_by("-date_added")
        )
        bool_dict["visibility_private"] = True

    elif sort_by == "date_modified":
        projects = (
            Project.objects.select_related("project_creator")
            .prefetch_related("bc_labels", "tk_labels")
            .filter(unique_id__in=project_ids)
            .exclude(unique_id__in=archived)
            .order_by("-date_modified")
        )
        bool_dict["date_modified"] = True

    page = paginate(request, projects, 10)

    if request.method == "GET":
        results = return_project_search_results(request, projects)

    context = {
        'projects': projects,
        'institution': institution,
        'member_role': member_role,
        'items': page,
        'results': results,
        'bool_dict': bool_dict,
        'subscription': subscription,
    }
    return render(request, "institutions/projects.html", context)


# Create Project
@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
@transaction.atomic
def create_project(request, pk, source_proj_uuid=None, related=None):
    institution = get_institution(pk)
    member_role = check_member_role(request.user, institution)
    name = get_users_name(request.user)
    notice_translations = get_notice_translations()
    notice_defaults = get_notice_defaults()
    
    if check_subscription(request, 'institution', pk):      
        return redirect('institution-projects', institution.id)
    
    subscription = Subscription.objects.get(institution=institution)
    if request.method == 'GET':
        form = CreateProjectForm(request.GET or None)
        formset = ProjectPersonFormset(queryset=ProjectPerson.objects.none())
    elif request.method == "POST":
        form = CreateProjectForm(request.POST)
        formset = ProjectPersonFormset(request.POST)
        subscription = Subscription.objects.get(institution=institution)

        if form.is_valid() and formset.is_valid():
            data = form.save(commit=False)
            data.project_creator = request.user

            # Define project_page field
            data.project_page = (
                f"{request.scheme}://{request.get_host()}/projects/{data.unique_id}"
            )

            # Handle multiple urls, save as array
            project_links = request.POST.getlist("project_urls")
            data.urls = project_links

            create_or_update_boundary(
                post_data=request.POST,
                entity=data
            )

            if subscription.project_count > 0:
                subscription.project_count -= 1
                subscription.save()

            data.save()

            if source_proj_uuid and not related:
                data.source_project_uuid = source_proj_uuid
                data.save()
                ProjectActivity.objects.create(
                    project=data,
                    activity=f'Sub Project "{data.title}" was added to Project by {name} | {institution.institution_name}',
                )

            if source_proj_uuid and related:
                source = Project.objects.get(unique_id=source_proj_uuid)
                data.related_projects.add(source)
                source.related_projects.add(data)
                source.save()
                data.save()

                ProjectActivity.objects.create(
                    project=data,
                    activity=f'Project "{source.title}" was connected to Project by {name} | {institution.institution_name}',
                )
                ProjectActivity.objects.create(
                    project=source,
                    activity=f'Project "{data.title}" was connected to Project by {name} | {institution.institution_name}',
                )

            # Create activity
            ProjectActivity.objects.create(
                project=data,
                activity=f"Project was created by {name} | {institution.institution_name}",
            )

            # Adds activity to Hub Activity
            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="Project Created",
                project_id=data.id,
                action_account_type="institution",
                institution_id=institution.id,
            )

            # Add project to institution projects
            creator = ProjectCreator.objects.select_related("institution").get(
                project=data
            )
            creator.institution = institution
            creator.save()

            # Create notices for project
            notices_selected = request.POST.getlist("checkbox-notice")
            translations_selected = request.POST.getlist("checkbox-translation")
            crud_notices(
                request,
                notices_selected,
                translations_selected,
                institution,
                data,
                None, False,
            )

            # Add selected contributors to the ProjectContributors object
            add_to_contributors(request, institution, data)

            # Project person formset
            instances = formset.save(commit=False)
            for instance in instances:
                if instance.name or instance.email:
                    instance.project = data
                    instance.save()

                # Send email to added person
                send_project_person_email(
                    request, instance.email, data.unique_id, institution
                )

            # Format and send notification about the created project
            truncated_project_title = str(data.title)[0:30]
            title = (
                f"A new project was created by {name}: {truncated_project_title} ..."
            )
            ActionNotification.objects.create(
                title=title,
                notification_type="Projects",
                sender=data.project_creator,
                reference_id=data.unique_id,
                institution=institution,
            )
            return redirect("institution-projects", institution.id)

    context = {
        "institution": institution,
        "notice_translations": notice_translations,
        "notice_defaults": notice_defaults,
        "form": form,
        "formset": formset,
        "member_role": member_role,
    }
    return render(request, "institutions/create-project.html", context)


@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def edit_project(request, pk, project_uuid):
    institution = get_institution(pk)
    project = Project.objects.get(unique_id=project_uuid)

    member_role = check_member_role(request.user, institution)
    form = EditProjectForm(request.POST or None, instance=project)
    formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
    contributors = ProjectContributors.objects.get(project=project)
    notices = Notice.objects.none()
    notice_translations = get_notice_translations()
    notice_defaults = get_notice_defaults()
    # Check to see if notice exists for this project and pass to template
    if Notice.objects.filter(project=project).exists():
        notices = Notice.objects.filter(project=project, archived=False)

    if request.method == 'POST':
        form = EditProjectForm(request.POST or None, instance=project)
        formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
        if form.is_valid() and formset.is_valid():
            has_changes = form.has_changed()
            data = form.save(commit=False)
            project_links = request.POST.getlist("project_urls")
            data.urls = project_links

            create_or_update_boundary(
                post_data=request.POST,
                entity=data
            )

            data.save()

            editor_name = get_users_name(request.user)
            ProjectActivity.objects.create(project=data, activity=f'Edits to Project were made by {editor_name}')
            communities = ProjectStatus.objects.filter( Q(status='pending') | Q(status__isnull=True),project=data, seen=True).select_related('community').order_by('community').distinct('community').values_list('community', flat=True)
            # Adds activity to Hub Activity
            HubActivity.objects.create(
                action_user_id=request.user.id,
                action_type="Project Edited",
                project_id=data.id,
                action_account_type="institution",
                institution_id=pk,
            )

            instances = formset.save(commit=False)
            for instance in instances:
                if instance.name or instance.email:
                    instance.project = project
                    instance.save()

            # Delete instances marked for deletion
            for instance in formset.deleted_objects:
                instance.delete()

            # Add selected contributors to the ProjectContributors object
            add_to_contributors(request, institution, data)

            notices_selected = request.POST.getlist('checkbox-notice')
            translations_selected = request.POST.getlist('checkbox-translation')
            has_changes = crud_notices(request, notices_selected, translations_selected, institution, data, notices, has_changes)
            
            if has_changes:
                send_action_notification_project_status(request, project, communities)
        return redirect('institution-project-actions', institution.id, project.unique_id)


    context = {
        "member_role": member_role,
        "institution": institution,
        "project": project,
        "notices": notices,
        "notice_defaults": notice_defaults,
        "form": form,
        "formset": formset,
        "contributors": contributors,
        "urls": project.urls,
        "notice_translations": notice_translations,
    }
    return render(request, "institutions/edit-project.html", context)


def project_actions(request, pk, project_uuid):
    try:
        institution = get_institution(pk)
        project = Project.objects.prefetch_related(
            "bc_labels",
            "tk_labels",
            "bc_labels__community",
            "tk_labels__community",
            "bc_labels__bclabel_translation",
            "tk_labels__tklabel_translation",
        ).get(unique_id=project_uuid)

        subscription = Subscription.objects.filter(institution=institution.id).first()
        member_role = check_member_role(request.user, institution)
        if (
            not member_role
            or not request.user.is_authenticated
            or not project.can_user_access(request.user)
        ):
            return redirect("view-project", project_uuid)
        else:
            notices = Notice.objects.filter(project=project, archived=False).exclude(notice_type='open_to_collaborate')
            creator = ProjectCreator.objects.get(project=project)
            statuses = ProjectStatus.objects.select_related("community").filter(
                project=project
            )
            comments = ProjectComment.objects.select_related("sender").filter(
                project=project
            )
            entities_notified = EntitiesNotified.objects.get(project=project)
            communities = Community.approved.all()
            activities = ProjectActivity.objects.filter(project=project).order_by(
                "-date"
            )
            sub_projects = Project.objects.filter(
                source_project_uuid=project.unique_id
            ).values_list("unique_id", "title")
            name = get_users_name(request.user)
            label_groups = return_project_labels_by_community(project)
            can_download = can_download_project(request, creator)

            # for related projects list
            project_ids = list(
                set(
                    institution.institution_created_project.all()
                    .values_list("project__unique_id", flat=True)
                    .union(
                        institution.institutions_notified.all().values_list(
                            "project__unique_id", flat=True
                        )
                    )
                    .union(
                        institution.contributing_institutions.all().values_list(
                            "project__unique_id", flat=True
                        )
                    )
                )
            )
            project_ids_to_exclude_list = list(
                project.related_projects.all().values_list("unique_id", flat=True)
            )  # projects that are currently related
            # exclude projects that are already related
            project_ids = list(set(project_ids).difference(project_ids_to_exclude_list))
            projects_to_link = (
                Project.objects.filter(unique_id__in=project_ids)
                .exclude(unique_id=project.unique_id)
                .order_by("-date_added")
                .values_list("unique_id", "title")
            )

            project_archived = False
            if ProjectArchived.objects.filter(
                project_uuid=project.unique_id, institution_id=institution.id
            ).exists():
                x = ProjectArchived.objects.get(
                    project_uuid=project.unique_id, institution_id=institution.id
                )
                project_archived = x.archived
            form = ProjectCommentForm(request.POST or None)

            communities_list = list(
                chain(
                    project.project_status.all().values_list(
                        "community__id", flat=True
                    ),
                )
            )

            if creator.community:
                communities_list.append(creator.community.id)

            communities_ids = list(set(communities_list))  # remove duplicate ids
            communities = Community.approved.exclude(id__in=communities_ids).order_by(
                "community_name"
            )

            if request.method == "POST":
                if request.POST.get("message"):
                    if form.is_valid():
                        data = form.save(commit=False)
                        data.project = project
                        data.sender = request.user
                        data.sender_affiliation = institution.institution_name
                        data.save()
                        send_action_notification_to_project_contribs(project)
                        return redirect('institution-project-actions', institution.id, project.unique_id)
                
                elif 'notify_btn' in request.POST:
                    if subscription.notification_count == 0:
                        messages.add_message(request, messages.ERROR, 'Your institution has reached its notification limit. '
                            'Please upgrade your subscription plan to notify more communities.')
                        return redirect('institution-project-actions', institution.id, project.unique_id)
                    # Set private project to contributor view
                    if project.project_privacy == "Private":
                        project.project_privacy = "Contributor"
                        project.save()

                    communities_selected = request.POST.getlist('selected_communities')
                    notification_count = subscription.notification_count
                    if notification_count == -1:
                        count = len(communities_selected)
                    else:
                        count = min(notification_count, len(communities_selected))
                    # Reference ID and title for notification
                    title = (
                        str(institution.institution_name)
                        + " has notified you of a Project."
                    )

                    for community_id in communities_selected[:count]:
                        # Add communities that were notified to entities_notified instance
                        community = Community.objects.get(id=community_id)
                        entities_notified.communities.add(community)

                        # Add activity
                        ProjectActivity.objects.create(
                            project=project,
                            activity=f"{community.community_name} was notified by {name}",
                        )

                        # Adds activity to Hub Activity
                        HubActivity.objects.create(
                            action_user_id=request.user.id,
                            action_type="Community Notified",
                            community_id=community.id,
                            institution_id=institution.id,
                            action_account_type="institution",
                            project_id=project.id,
                        )

                        # Create project status, first comment and  notification
                        ProjectStatus.objects.create(
                            project=project, community=community, seen=False
                        )  # Creates a project status for each community
                        ActionNotification.objects.create(
                            community=community,
                            notification_type="Projects",
                            reference_id=str(project.unique_id),
                            sender=request.user,
                            title=title,
                        )
                        entities_notified.save()

                        # Create email 
                        send_email_notice_placed(request, project, community, institution)
                    
                    # commenting this because we are not showing notification on project_action page
                    if subscription.notification_count > 0:
                        subscription.notification_count -= notification_count
                        subscription.save()
                    return redirect('institution-project-actions', institution.id, project.unique_id)
                elif 'link_projects_btn' in request.POST:
                    selected_projects = request.POST.getlist('projects_to_link')

                    activities = []
                    for uuid in selected_projects:
                        project_to_add = Project.objects.get(unique_id=uuid)
                        project.related_projects.add(project_to_add)
                        project_to_add.related_projects.add(project)
                        project_to_add.save()

                        activities.append(
                            ProjectActivity(
                                project=project,
                                activity=f'Project "{project_to_add.title}" was connected to Project by {name} | {institution.institution_name}',
                            )
                        )
                        activities.append(
                            ProjectActivity(
                                project=project_to_add,
                                activity=f'Project "{project.title}" was connected to Project by {name} | {institution.institution_name}',
                            )
                        )

                    ProjectActivity.objects.bulk_create(activities)
                    project.save()
                    return redirect(
                        "institution-project-actions", institution.id, project.unique_id
                    )

                elif "delete_project" in request.POST:
                    return redirect(
                        "inst-delete-project", institution.id, project.unique_id
                    )

                elif "remove_contributor" in request.POST:
                    contribs = ProjectContributors.objects.get(project=project)
                    contribs.institutions.remove(institution)
                    contribs.save()
                    return redirect(
                        "institution-project-actions", institution.id, project.unique_id
                    )

            context = {
                "member_role": member_role,
                "institution": institution,
                "project": project,
                "notices": notices,
                "creator": creator,
                "form": form,
                "communities": communities,
                "statuses": statuses,
                "comments": comments,
                "activities": activities,
                "project_archived": project_archived,
                "sub_projects": sub_projects,
                "projects_to_link": projects_to_link,
                "label_groups": label_groups,
                "can_download": can_download,
                "subscription": subscription,
            }
            return render(request, "institutions/project-actions.html", context)
    except:
        raise Http404()


@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def archive_project(request, pk, project_uuid):
    if not ProjectArchived.objects.filter(
        institution_id=pk, project_uuid=project_uuid
    ).exists():
        ProjectArchived.objects.create(
            institution_id=pk, project_uuid=project_uuid, archived=True
        )
    else:
        archived_project = ProjectArchived.objects.get(
            institution_id=pk, project_uuid=project_uuid
        )
        if archived_project.archived:
            archived_project.archived = False
        else:
            archived_project.archived = True
        archived_project.save()
    return redirect("institution-project-actions", pk, project_uuid)


@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
@transaction.atomic
def delete_project(request, pk, project_uuid):
    institution = get_institution(pk)
    project = Project.objects.get(unique_id=project_uuid)
    subscription = Subscription.objects.get(institution=institution)

    delete_action_notification(project.unique_id)
    project.delete()

    if subscription.project_count >= 0:
        subscription.project_count +=1
        subscription.save()
    return redirect('institution-projects', institution.id)

@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def unlink_project(request, pk, target_proj_uuid, proj_to_remove_uuid):
    institution = get_institution(pk)
    target_project = Project.objects.get(unique_id=target_proj_uuid)
    project_to_remove = Project.objects.get(unique_id=proj_to_remove_uuid)
    target_project.related_projects.remove(project_to_remove)
    project_to_remove.related_projects.remove(target_project)
    target_project.save()
    project_to_remove.save()
    name = get_users_name(request.user)
    ProjectActivity.objects.create(
        project=project_to_remove,
        activity=f'Connection was removed between Project "{project_to_remove}" and Project "{target_project}" by {name}',
    )
    ProjectActivity.objects.create(
        project=target_project,
        activity=f'Connection was removed between Project "{target_project}" and Project "{project_to_remove}" by {name}',
    )
    return redirect(
        "institution-project-actions", institution.id, target_project.unique_id
    )


@login_required(login_url="login")
@member_required(roles=["admin", "editor", "viewer"])
def connections(request, pk):
    institution = get_institution(pk)
    member_role = check_member_role(request.user, institution)
    institutions = Institution.objects.none()

    # Researcher contributors
    researcher_ids = institution.contributing_institutions.exclude(
        researchers__id=None
    ).values_list("researchers__id", flat=True)
    researchers = Researcher.objects.select_related("user").filter(
        id__in=researcher_ids
    )

    # Community contributors
    community_ids = institution.contributing_institutions.exclude(
        communities__id=None
    ).values_list("communities__id", flat=True)
    communities = (
        Community.objects.select_related("community_creator")
        .prefetch_related("admins", "editors", "viewers")
        .filter(id__in=community_ids)
    )

    # Institution contributors
    project_ids = institution.contributing_institutions.values_list(
        "project__unique_id", flat=True
    )
    contributors = ProjectContributors.objects.filter(
        project__unique_id__in=project_ids
    ).values_list("institutions__id", flat=True)
    institutions = (
        Institution.objects.select_related("institution_creator")
        .prefetch_related("admins", "editors", "viewers")
        .filter(id__in=contributors)
        .exclude(id=institution.id)
    )

    context = {
        "member_role": member_role,
        "institution": institution,
        "communities": communities,
        "researchers": researchers,
        "institutions": institutions,
    }
    return render(request, "institutions/connections.html", context)


@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def connect_service_provider(request, pk):
    try:
        envi = dev_prod_or_local(request.get_host())
        institution = get_institution(pk)
        member_role = check_member_role(request.user, institution)
        if request.method == "GET":
            service_providers = get_certified_service_providers(request)
            connected_service_providers_ids = ServiceProviderConnections.objects.filter(
                institutions=institution
            ).values_list('service_provider', flat=True)
            connected_service_providers = service_providers.filter(id__in=connected_service_providers_ids)
            other_service_providers = service_providers.exclude(id__in=connected_service_providers_ids)

        elif request.method == "POST":
            if "connectServiceProvider" in request.POST:
                if institution.is_subscribed:
                    service_provider_id = request.POST.get('connectServiceProvider')
                    connection_reference_id = f"{service_provider_id}:{institution.id}_i"

                    if ServiceProviderConnections.objects.filter(
                            service_provider=service_provider_id).exists():
                        # Connect institution to existing Service Provider connection
                        sp_connection = ServiceProviderConnections.objects.get(
                            service_provider=service_provider_id
                        )
                        sp_connection.institutions.add(institution)
                        sp_connection.save()
                    else:
                        # Create new Service Provider Connection and add institution
                        service_provider = ServiceProvider.objects.get(id=service_provider_id)
                        sp_connection = ServiceProviderConnections.objects.create(
                            service_provider = service_provider
                        )
                        sp_connection.institutions.add(institution)
                        sp_connection.save()

                    # Delete instances of disconnect Notifications
                    delete_action_notification(connection_reference_id)

                    # Send notification of connection to Service Provider
                    target_org = sp_connection.service_provider
                    title = f"{institution.institution_name} has connected to {target_org.name}"
                    send_simple_action_notification(
                        None, target_org, title, "Connections", connection_reference_id
                    )
                else:
                    messages.add_message(
                        request, messages.ERROR,
                        'Your account must be subscribed to connect to Service Providers.'
                    )

            elif "disconnectServiceProvider" in request.POST:
                service_provider_id = request.POST.get('disconnectServiceProvider')
                connection_reference_id = f"{service_provider_id}:{institution.id}_i"

                sp_connection = ServiceProviderConnections.objects.get(
                    service_provider=service_provider_id
                )
                sp_connection.institutions.remove(institution)
                sp_connection.save()

                # Delete instances of the connection notification
                delete_action_notification(connection_reference_id)

                # Send notification of disconneciton to Service Provider
                target_org = sp_connection.service_provider
                title = f"{institution.institution_name} has been disconnected from " \
                        f"{target_org.name}"
                send_simple_action_notification(
                    None, target_org, title, "Connections", connection_reference_id
                )

            return redirect("institution-connect-service-provider", institution.id)

        context = {
            'member_role': member_role,
            'institution': institution,
            'other_service_providers': other_service_providers,
            'connected_service_providers': connected_service_providers,
            'envi': envi
        }
        return render(request, 'account_settings_pages/_connect-service-provider.html', context)

    except:
        raise Http404()

@login_required(login_url="login")
@member_required(roles=["admin", "editor"])
def account_preferences(request, pk):
    try:
        institution = get_institution(pk)
        member_role = check_member_role(request.user, institution)

        if request.method == "POST":

            # Set Show/Hide account in Service Provider connections
            if request.POST.get('show_sp_connection') == 'on':
                institution.show_sp_connection = True

            elif request.POST.get('show_sp_connection') == None:
                institution.show_sp_connection = False

            # Set project privacy settings for Service Provider connections
            institution.sp_privacy = request.POST.get('sp_privacy')

            institution.save()

            messages.add_message(
                request, messages.SUCCESS, 'Your preferences have been updated!'
            )

            return redirect("preferences-institution", institution.id)

        context = {
            'member_role': member_role,
            'institution': institution,
        }
        return render(request, 'account_settings_pages/_preferences.html', context)

    except Institution.DoesNotExist:
        raise Http404()


@force_maintenance_mode_off
def embed_otc_notice(request, pk):
    layout = request.GET.get("lt")
    lang = request.GET.get("lang")
    align = request.GET.get("align")

    institution = Institution.objects.get(id=pk)
    otc_notices = OpenToCollaborateNoticeURL.objects.filter(institution=institution)

    context = {
        "layout": layout,
        "lang": lang,
        "align": align,
        "otc_notices": otc_notices,
        "institution": institution,
    }

    response = render(request, "partials/_embed.html", context)
    response["Content-Security-Policy"] = "frame-ancestors https://*"

    return response

# Create API Key
@login_required(login_url="login")
@member_required(roles=["admin"])
@transaction.atomic
def api_keys(request, pk):
    institution = get_institution(pk)
    member_role = check_member_role(request.user, institution)
    remaining_api_key_count = 0
    envi = dev_prod_or_local(request.get_host())

    try:
        if institution.is_subscribed:
            subscription = Subscription.objects.get(institution=institution)
            remaining_api_key_count = subscription.api_key_count

        if request.method == 'GET':
            form = APIKeyGeneratorForm(request.GET or None)
            account_keys = AccountAPIKey.objects.filter(institution=institution).exclude(
                Q(expiry_date__lt=timezone.now()) | Q(revoked=True)
            ).values_list("prefix", "name", "encrypted_key")

        elif request.method == "POST":
            if "generate_api_key" in request.POST:
                if institution.is_subscribed and remaining_api_key_count == 0:
                    messages.add_message(request, messages.ERROR, 'Your institution has reached its API Key limit. '
                                        'Please upgrade your subscription plan to create more API Keys.')
                    return redirect("institution-api-key", institution.id)
                form = APIKeyGeneratorForm(request.POST)

                if institution.is_subscribed:
                    if form.is_valid():
                        api_key, key = AccountAPIKey.objects.create_key(
                            name = form.cleaned_data["name"],
                            institution_id = institution.id
                        )
                        prefix = key.split(".")[0]
                        encrypted_key = encrypt_api_key(key)
                        AccountAPIKey.objects.filter(prefix=prefix).update(encrypted_key=encrypted_key)

                        if subscription.api_key_count > 0:
                            subscription.api_key_count -= 1
                            subscription.save()
                    else:
                        messages.add_message(request, messages.ERROR, 'Please enter a valid API Key name.')
                        return redirect("institution-api-key", institution.id)

                else:
                    messages.add_message(request, messages.ERROR, 'Your institution is not subscribed. '
                                        'You must have an active subscription to create more API Keys.')
                    return redirect("institution-api-key", institution.id)

                return redirect("institution-api-key", institution.id)

            elif "delete_api_key" in request.POST:
                prefix = request.POST['delete_api_key']
                api_key = AccountAPIKey.objects.filter(prefix=prefix)
                api_key.delete()

                if institution.is_subscribed and subscription.api_key_count >= 0:
                    subscription.api_key_count +=1
                    subscription.save()

                return redirect("institution-api-key", institution.id)

        context = {
            "institution" : institution,
            "form" : form,
            "account_keys" : account_keys,
            "member_role" : member_role,
            "remaining_api_key_count" : remaining_api_key_count,
            "envi": envi,
        }
        return render(request, 'account_settings_pages/_api-keys.html', context)
    except:
        raise Http404()
    
@login_required(login_url="login")
def create_institution_subscription(request, pk):
    try:
        institute = get_institution(pk)
        env = dev_prod_or_local(request.get_host())
        initial_data = {
            "first_name": request.user._wrapped.first_name,
            "last_name": request.user._wrapped.last_name,
            "email": request.user._wrapped.email,
            "organization_name": institute.institution_name,
        }
        subscription_form = SubscriptionForm(initial=initial_data)
        subscription_form.fields['organization_name'].widget.attrs.update({"class": "w-100 readonly-input"})

        if request.method == "POST":
            if validate_recaptcha(request):
                mutable_post_data = request.POST.copy()
                subscription_data = {
                    "first_name": request.POST['first_name'],
                    "last_name": request.POST['last_name'],
                    "email": request.POST['email'],
                    "account_type": "institution_account",
                    "inquiry_type": request.POST['inquiry_type'],
                    "organization_name": request.POST['organization_name'],
                }
                
                mutable_post_data.update(subscription_data)
                subscription_form = SubscriptionForm(mutable_post_data)
                if subscription_form.is_valid() and env != 'SANDBOX':
                    handle_confirmation_and_subscription(request, subscription_form, institute, env)
                    return redirect('dashboard')
                else:
                    messages.add_message(
                        request, messages.ERROR, "Something went wrong. Please Try again later.",
                    )
                    return redirect('dashboard')
        return render(
            request, "account_settings_pages/_subscription-form.html", {
                "subscription_form": subscription_form,
                'institution': institute
            }
        )
    except Institution.DoesNotExist:
        return render(request, '404.html', status=404)