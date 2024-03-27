# Captcha validation imports
import urllib

# For emails
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.utils.encoding import force_str, force_bytes
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages, auth
from django.views.generic import View
from django.contrib.auth.views import (
    PasswordChangeForm,
    SetPasswordForm,
    PasswordResetView,
)
from django.core.paginator import Paginator
from django.db.models import Q

from allauth.socialaccount.views import SignupView, ConnectionsView
from allauth.socialaccount.models import SocialAccount
from django.core import serializers

from rest_framework_api_key.models import APIKey
from unidecode import unidecode

from institutions.models import Institution
from localcontexts.utils import dev_prod_or_local
from researchers.models import Researcher
from .decorators import unauthenticated_user

from communities.models import InviteMember, Community
from helpers.models import HubActivity
from projects.models import Project

from researchers.utils import is_user_researcher
from helpers.utils import accept_member_invite
from helpers.utils import validate_email, validate_recaptcha, create_salesforce_account_or_lead

from helpers.emails import (send_activation_email, generate_token,
                            resend_activation_email, send_welcome_email,
                            send_email_verification, send_invite_user_email,
                            add_to_newsletter_mailing_list,
                            get_newsletter_member_info,
                            unsubscribe_from_mailing_list)
from .models import SignUpInvitation, Profile, UserAffiliation
from .forms import (RegistrationForm, ResendEmailActivationForm,
                    CustomPasswordResetForm, UserCreateProfileForm,
                    ProfileCreationForm, UserUpdateForm, ProfileUpdateForm,
                    SignUpInvitationForm)

from .utils import (get_next_path, get_users_name, return_registry_accounts,
                    manage_mailing_list)

from helpers.emails import (
    send_activation_email,
    generate_token,
    resend_activation_email,
    send_welcome_email,
    send_email_verification,
    send_invite_user_email,
    add_to_newsletter_mailing_list,
    get_newsletter_member_info,
    unsubscribe_from_mailing_list,
)
from .models import SignUpInvitation, Profile, UserAffiliation
from .forms import (
    RegistrationForm,
    ResendEmailActivationForm,
    CustomPasswordResetForm,
    UserCreateProfileForm,
    ProfileCreationForm,
    UserUpdateForm,
    ProfileUpdateForm,
    SignUpInvitationForm,
    SubscriptionForm,
)

from .utils import (
    get_next_path,
    get_users_name,
    return_registry_accounts,
    manage_mailing_list,
    institute_account_subscription,
)


@unauthenticated_user
def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            if validate_recaptcha(request):
                user = form.save(commit=False)

                if User.objects.filter(email=user.email).exists():
                    messages.error(
                        request, "A user with this email already exists."
                    )
                    return redirect("register")
                elif User.objects.filter(
                    username__iexact=user.username.lower()
                ).exists():
                    messages.error(
                        request, "A user with this username already exists."
                    )
                    return redirect("register")
                elif not validate_email(email=user.email):
                    messages.error(request, "The email you entered is invalid")
                    return redirect("register")
                else:
                    user.is_active = False
                    user.save()

                    # If SignupInvite instances exist, delete them
                    if SignUpInvitation.objects.filter(
                        email=user.email
                    ).exists():
                        for invite in SignUpInvitation.objects.filter(
                            email=user.email
                        ):
                            invite.delete()

                    send_activation_email(request, user)
                    HubActivity.objects.create(
                        action_user_id=user.id, action_type="New User"
                    )
                    return redirect("verify")
            else:
                messages.error(request, "Invalid reCAPTCHA. Please try again.")

            return redirect("register")
    return render(request, "accounts/register.html", {"form": form})


class ActivateAccountView(View):

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (Exception,):
            user = None

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(
                request,
                messages.INFO,
                "Profile activation successful. You are now able to login.",
            )
            return redirect("login")
        return render(request, "snippets/activate-failed.html", status=401)


@unauthenticated_user
def verify(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect("/dashboard")

    form = ResendEmailActivationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            active_users = User._default_manager.filter(
                **{
                    "%s__iexact"
                    % User.get_email_field_name(): form.cleaned_data["email"],
                    "is_active": False,
                }
            )

            if active_users:
                resend_activation_email(request, active_users)
                messages.add_message(
                    request, messages.INFO, "Activation email sent!"
                )
                return redirect("verify")
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Email did not match any registration email.",
                )
                return redirect("verify")
    return render(request, "accounts/verify.html", {"form": form})


@unauthenticated_user
def login(request):
    envi = dev_prod_or_local(request.get_host())

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(request, username=username, password=password)

        if user is None:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

        if user is not None and user.check_password(password):
            if user.is_active:
                if not user.last_login:
                    auth.login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    # Welcome email
                    send_welcome_email(request, user)
                    return redirect("create-profile")
                else:
                    auth.login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    return redirect(
                        get_next_path(request, default_path="dashboard")
                    )
            else:
                if not user.last_login:
                    messages.error(
                        request,
                        "Your account is not active yet. "
                        "Please verify your email.",
                    )
                    if SignUpInvitation.objects.filter(
                        email=user.email
                    ).exists():
                        for invite in SignUpInvitation.objects.filter(
                            email=user.email
                        ):
                            invite.delete()

                    send_activation_email(request, user)
                    return redirect("verify")
                else:
                    messages.error(
                        request,
                        "Your account is not active. "
                        "Please contact support@localcontexts.org.",
                    )
                    return redirect("login")
        else:
            messages.error(
                request, "Your username or password does not match an account."
            )
            return redirect("login")
    else:
        return render(request, "accounts/login.html", {"envi": envi})


@login_required(login_url="login")
def logout(request):
    if request.method == "POST":
        auth.logout(request)
        return redirect("login")


def landing(request):
    return redirect("login")


@login_required(login_url="login")
def select_account(request):
    return render(request, "accounts/select-account.html")


class CustomSocialSignupView(SignupView):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(
                request,
                "You have already created your account using "
                "username and password. Please use those to login instead. "
                "You can still connect your account with "
                "Google once you login.",
            )
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)


class CustomSocialConnectionsView(ConnectionsView):

    def dispatch(self, request, *args, **kwargs):
        provider = kwargs["provider"]
        social_account = SocialAccount.objects.filter(
            provider=provider, user=request.user
        ).first()
        has_password = request.user.has_usable_password()
        if social_account and has_password:
            social_account.delete()
            messages.info(request, "The social account has been disconnected.")
            return redirect("link-account")
        else:
            messages.error(
                request, "Please set password first to unlink an account."
            )
            return redirect("link-account")
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    email_template_name = "password_reset"
    from_email = settings.EMAIL_HOST_USER
    template_name = "accounts/password-reset.html"
    form_class = CustomPasswordResetForm

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@login_required(login_url="login")
def dashboard(request):
    user = request.user
    profile = user.user_profile
    researcher = is_user_researcher(user)

    affiliation = (
        user.user_affiliations.prefetch_related(
            "communities",
            "institutions",
            "communities__admins",
            "communities__editors",
            "communities__viewers",
            "institutions__admins",
            "institutions__editors",
            "institutions__viewers",
        )
        .all()
        .first()
    )

    user_communities = affiliation.communities.all()
    user_institutions = affiliation.institutions.all()
    unsubscribed_institute = Institution.objects.filter(
        institution_creator=user, is_subscribed=False
    ).first()

    if request.method == "POST":
        profile.onboarding_on = False
        profile.save()

    context = {
        "profile": profile,
        "user_communities": user_communities,
        "user_institutions": user_institutions,
        "researcher": researcher,
        "unsubscribed_institute": unsubscribed_institute,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required(login_url="login")
def onboarding_on(request):
    request.user.user_profile.onboarding_on = True
    request.user.user_profile.save()
    return redirect("dashboard")


@login_required(login_url="login")
def create_profile(request):
    if request.method == "POST":
        user_form = UserCreateProfileForm(request.POST, instance=request.user)
        profile_form = ProfileCreationForm(
            request.POST, instance=request.user.user_profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("select-account")
    else:
        user_form = UserCreateProfileForm(instance=request.user)
        profile_form = ProfileCreationForm(instance=request.user.user_profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "accounts/create-profile.html", context)


@login_required(login_url="login")
def update_profile(request):
    profile = Profile.objects.select_related("user").get(user=request.user)

    if request.method == "POST":
        old_email = request.user.email
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.user_profile
        )
        new_email = user_form.data["email"]

        if new_email != old_email and new_email != "" and user_form.is_valid():
            user_form.instance.email = old_email
            profile_form.save()
            user_form.save()
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(request.user)
            encoded_token = urlsafe_base64_encode(
                force_bytes(f"{token} {new_email} {request.user.id}")
            )
            verification_url = (
                f"http://{get_current_site(request).domain}"
                f"/confirm-email/{request.user.pk}"
                f"/{encoded_token}"
            )
            send_email_verification(
                request, old_email, new_email, verification_url
            )
            messages.add_message(
                request,
                messages.INFO,
                f"A verification email has been sent to {new_email}.",
            )
            return redirect("update-profile")
        elif user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            return redirect("update-profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.user_profile)

    context = {
        "profile": profile,
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "accounts/update-profile.html", context)


@login_required(login_url="login")
def confirm_email(request, uidb64, token):
    try:
        decoded_token = urlsafe_base64_decode(token).decode("utf-8")
        new_token, new_email, user_id_str = decoded_token.split(" ")
    except ValueError:
        messages.add_message(
            request, messages.ERROR, "Invalid Verification token."
        )
        return redirect("login")
    new_token = new_token.strip()
    new_email = new_email.strip()
    user_id = user_id_str.strip()

    if not User.objects.filter(pk=user_id).exists():
        messages.add_message(request, messages.ERROR, "User not found.")
        return redirect("login")
    user = User.objects.get(pk=user_id)
    user.email = new_email
    user.save()
    messages.add_message(
        request, messages.SUCCESS, "Email updated Successfully."
    )
    return redirect("dashboard")


@login_required(login_url="login")
def change_password(request):
    profile = Profile.objects.select_related("user").get(user=request.user)
    has_usable_password = request.user.has_usable_password()

    if not has_usable_password:
        form = SetPasswordForm(request.user, request.POST or None)
    else:
        form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.add_message(
                request, messages.SUCCESS, "Password successfully changed!"
            )
            return redirect("change-password")
        else:
            messages.add_message(
                request, messages.ERROR, "Something went wrong."
            )
            return redirect("change-password")
    return render(
        request,
        "accounts/change-password.html",
        {"profile": profile, "form": form},
    )


@login_required(login_url="login")
def deactivate_user(request):
    profile = Profile.objects.select_related("user").get(user=request.user)
    if request.method == "POST":
        user = request.user
        user.is_active = False
        user.save()
        auth.logout(request)
        messages.add_message(
            request,
            messages.INFO,
            "Your account has been deactivated. "
            "If this was a mistake please contact support@localcontexts.org.",
        )
        return redirect("login")
    return render(request, "accounts/deactivate.html", {"profile": profile})


@login_required(login_url="login")
def manage_organizations(request):
    profile = Profile.objects.select_related("user").get(user=request.user)
    affiliations = UserAffiliation.objects.prefetch_related(
        "communities",
        "institutions",
        "communities__community_creator",
        "institutions__institution_creator",
    ).get(user=request.user)
    researcher = Researcher.objects.none()
    users_name = get_users_name(request.user)
    if Researcher.objects.filter(user=request.user).exists():
        researcher = Researcher.objects.get(user=request.user)
    return render(
        request,
        "accounts/manage-orgs.html",
        {
            "profile": profile,
            "affiliations": affiliations,
            "researcher": researcher,
            "users_name": users_name,
        },
    )


@login_required(login_url="login")
def link_account(request):
    has_social_account = SocialAccount.objects.filter(
        user=request.user
    ).exists()
    provider = None
    if has_social_account:
        social_account = SocialAccount.objects.filter(
            user=request.user
        ).first()
        provider = social_account.provider

    return render(
        request,
        "accounts/link-account.html",
        {"socialaccount": has_social_account, "provider": provider},
    )


@login_required(login_url="login")
def member_invitations(request):
    profile = Profile.objects.select_related("user").get(user=request.user)
    member_invites = InviteMember.objects.filter(receiver=request.user)

    if request.method == "POST":
        invite_id = request.POST.get("invite_id")
        accept_member_invite(request, invite_id)
        return redirect("member-invitations")

    context = {
        "profile": profile,
        "member_invites": member_invites,
    }
    return render(request, "accounts/member-invitations.html", context)


@login_required(login_url="login")
def delete_member_invitation(request, pk):
    profile = Profile.objects.select_related("user").get(user=request.user)
    member_invites = InviteMember.objects.filter(receiver=request.user)

    target_member_invite = InviteMember.objects.get(id=pk)
    target_member_invite.delete()

    context = {
        "profile": profile,
        "member_invites": member_invites,
    }
    return render(request, "accounts/member-invitations.html", context)


@login_required(login_url="login")
def invite_user(request):
    # use internally referred path, otherwise use the default path
    default_path = "invite"
    referred_path = request.headers.get("Referer", default_path)
    selected_path = urllib.parse.urlparse(referred_path).path

    invite_form = SignUpInvitationForm(request.POST or None)
    if request.method == "POST":
        if invite_form.is_valid():
            data = invite_form.save(commit=False)
            data.sender = request.user

            if User.objects.filter(email=data.email).exists():
                messages.add_message(
                    request, messages.ERROR, "This user is already in the Hub."
                )
                return redirect(selected_path)
            else:
                if SignUpInvitation.objects.filter(email=data.email).exists():
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "An invitation has already been sent to this email.",
                    )
                    return redirect(selected_path)
                else:
                    messages.add_message(
                        request, messages.SUCCESS, "Invitation sent!"
                    )
                    send_invite_user_email(request, data)
                    data.save()
                    return redirect(selected_path)

    # when validation fails and selected_path is not the default
    # redirect to selected path
    if selected_path.strip("/") != default_path:
        return redirect(selected_path)

    return render(
        request, "accounts/invite.html", {"invite_form": invite_form}
    )


def registry(request, filtertype=None):
    try:
        c = (
            Community.approved.select_related("community_creator")
            .prefetch_related("admins", "editors", "viewers")
            .all()
            .order_by("community_name")
        )
        i = (
            Institution.approved.select_related("institution_creator")
            .prefetch_related("admins", "editors", "viewers")
            .all()
            .order_by("institution_name")
        )
        r = (
            Researcher.objects.select_related("user")
            .all()
            .order_by("user__username")
        )

        if ("q" in request.GET) and (filtertype is not None):
            q = request.GET.get("q")
            return redirect("/registry/?q=" + q)

        elif ("q" in request.GET) and (filtertype is None):
            q = request.GET.get("q")
            q = unidecode(q)  # removes accents from search query

            # Filter's accounts by the search query,
            # showing results that match with or without accents
            c = c.filter(community_name__unaccent__icontains=q)
            i = i.filter(institution_name__unaccent__icontains=q)
            r = r.filter(
                Q(user__username__unaccent__icontains=q)
                | Q(user__first_name__unaccent__icontains=q)
                | Q(user__last_name__unaccent__icontains=q)
            )

            cards = return_registry_accounts(c, r, i)

            p = Paginator(cards, 5)

        else:
            if filtertype == "communities":
                cards = c
            elif filtertype == "institutions":
                cards = i
            elif filtertype == "researchers":
                cards = r
            elif filtertype == "otc":
                researchers_with_otc = r.filter(
                    otc_researcher_url__isnull=False
                ).distinct()
                institutions_with_otc = i.filter(
                    otc_institution_url__isnull=False
                ).distinct()
                cards = return_registry_accounts(
                    None, researchers_with_otc, institutions_with_otc
                )
            else:
                cards = return_registry_accounts(c, r, i)

            p = Paginator(cards, 5)

        page_num = request.GET.get("page", 1)
        page = p.page(page_num)

        context = {
            "researchers": r,
            "communities": c,
            "institutions": i,
            "items": page,
            "filtertype": filtertype,
        }

        return render(request, "accounts/registry.html", context)

    except Exception:
        raise Http404()


def projects_board(request, filtertype=None):
    try:
        approved_institutions = Institution.objects.filter(
            is_approved=True
        ).values_list("id", flat=True)
        approved_communities = Community.objects.filter(
            is_approved=True
        ).values_list("id", flat=True)

        public_projects_filter = Q(project_privacy="Public")
        institution_projects_filter = Q(
            project_creator_project__institution__in=approved_institutions
        )
        community_projects_filter = Q(
            project_creator_project__community__in=approved_communities
        )
        researcher_projects_filter = Q(
            project_creator_project__researcher__user__isnull=False
        )

        projects = (
            Project.objects.filter(
                public_projects_filter
                & (
                    institution_projects_filter
                    | community_projects_filter
                    | researcher_projects_filter
                )
            )
            .select_related("project_creator")
            .order_by("-date_modified")
        )

        if ("q" in request.GET) and (filtertype is not None):
            q = request.GET.get("q")
            return redirect("/projects-board/?q=" + q)
        elif ("q" in request.GET) and (filtertype is None):
            q = request.GET.get("q")
            q = unidecode(q)  # removes accents from search query

            # Filter's accounts by the search query,
            # showing results that match with or without accents
            results = projects.filter(
                Q(title__unaccent__icontains=q)
                | Q(description__unaccent__icontains=q)
            )

            p = Paginator(results, 10)
        else:
            if filtertype == "labels":
                results = projects.filter(
                    Q(bc_labels__isnull=False) | Q(tk_labels__isnull=False)
                )
            elif filtertype == "notices":
                results = projects.filter(
                    project_notice__archived=False
                ).distinct()
            else:
                results = projects

            p = Paginator(results, 10)

        page_num = request.GET.get("page", 1)
        page = p.page(page_num)

        context = {
            "projects": projects,
            "items": page,
            "filtertype": filtertype,
        }
        return render(request, "accounts/projects-board.html", context)
    except Exception:
        raise Http404()


# Hub stats page
def hub_counter(request):
    return redirect("/admin/dashboard/")


def newsletter_subscription(request):
    environment = dev_prod_or_local(request.get_host())

    if environment == 'PROD' or 'localhost' in request.get_host():
        if request.method == 'POST':
            if 'topic' not in request.POST:
                messages.add_message(request, messages.ERROR,
                                     'Please select at least one topic.')
                return redirect('newsletter-subscription')
            else:
                if validate_recaptcha(request):
                    first_name = request.POST['first_name']
                    last_name = request.POST['last_name']
                    name = str(first_name) + str(' ') + str(last_name)
                    email = request.POST['email']
                    emailb64 = urlsafe_base64_encode(force_bytes(email))
                    variables = manage_mailing_list(
                        request, first_name, emailb64
                    )
                    add_to_newsletter_mailing_list(
                        str(email), str(name), str(variables)
                    )
                    message_text = mark_safe(
                        "Thank&nbsp;you&nbsp;an&nbsp;"
                        "email&nbsp;has&nbsp;been&nbsp;sent"
                    )
                    messages.add_message(
                        request, messages.SUCCESS, message_text
                    )
                    return render(
                        request,
                        "accounts/newsletter-subscription.html",
                        {"emailb64": emailb64},
                    )
                else:
                    messages.error(
                        request, "Invalid reCAPTCHA. Please try again."
                    )

        return render(request, "accounts/newsletter-subscription.html")
    else:
        return redirect("login")


def newsletter_unsubscription(request, emailb64):
    environment = dev_prod_or_local(request.get_host())

    if environment == "PROD" or "localhost" in request.get_host():
        try:
            email = force_str(urlsafe_base64_decode(emailb64))
            response = get_newsletter_member_info(email)
            data = response.json()
            member_info = data["member"]
            name = member_info["name"]
            variables = member_info["vars"]
            subscribed = member_info["subscribed"]
            if subscribed is True:
                for item in variables:
                    if item == "tech":
                        tech = variables[item]
                    if item == "news":
                        news = variables[item]
                    if item == "events":
                        events = variables[item]
                    if item == "notice":
                        notice = variables[item]
                    if item == "labels":
                        labels = variables[item]
                    if item == "first_name":
                        first_name = variables[item]

                context = {
                    "email": email,
                    "tech": tech,
                    "news": news,
                    "events": events,
                    "notice": notice,
                    "labels": labels,
                    "subscribed": subscribed,
                }
            else:
                context = {"subscribed": subscribed}

            if request.method == "POST":
                if "updatebtn" in request.POST:
                    if "unsubscribe" in request.POST:
                        unsubscribe_from_mailing_list(str(email), str(name))
                        messages.add_message(
                            request,
                            messages.SUCCESS,
                            "You unsubscribed successfully!",
                        )
                        return redirect(
                            "newsletter-unsubscription", emailb64=emailb64
                        )
                    elif "topic" in request.POST:
                        variables = manage_mailing_list(
                            request, first_name, email
                        )
                        add_to_newsletter_mailing_list(
                            str(email), str(name), str(variables)
                        )
                        messages.add_message(
                            request,
                            messages.SUCCESS,
                            "Your preferences have been updated!",
                        )
                        return redirect(
                            "newsletter-unsubscription", emailb64=emailb64
                        )
                    else:
                        messages.add_message(
                            request,
                            messages.ERROR,
                            "Please select at least one option.",
                        )
                        return redirect(
                            "newsletter-unsubscription", emailb64=emailb64
                        )
            return render(
                request, "accounts/newsletter-unsubscription.html", context
            )
        except Exception:
            raise Http404()

    else:
        return redirect("login")


@login_required(login_url="login")
def api_keys(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if "generatebtn" in request.POST:
            api_key, key = APIKey.objects.create_key(
                name=request.user.username
            )
            profile.api_key = key
            profile.save()
            messages.add_message(
                request, messages.SUCCESS, "API Key generated!"
            )
            page_key = profile.api_key
            return redirect("api-key")

        elif "hidebtn" in request.POST:
            return redirect("api-key")

        elif "continueKeyDeleteBtn" in request.POST:
            api_key = APIKey.objects.get(name=request.user.username)
            api_key.delete()
            profile.api_key = None
            profile.save()
            messages.add_message(request, messages.SUCCESS, "API Key deleted!")
            return redirect("api-key")

        elif "copybtn" in request.POST:
            messages.add_message(request, messages.SUCCESS, "Copied!")
            return redirect("api-key")

        elif "showbtn" in request.POST:
            page_key = profile.api_key
            context = {"api_key": page_key, "has_key": True}
            request.session["keyvisible"] = True
            return redirect("api-key")

    keyvisible = request.session.pop("keyvisible", False)

    if request.method == "GET":
        if profile.api_key is None:
            context = {"has_key": False}
            return render(request, "accounts/apikey.html", context)
        elif profile.api_key is not None and keyvisible is not False:
            context = {
                "has_key": True,
                "keyvisible": keyvisible,
                "api_key": profile.api_key,
            }
            return render(request, "accounts/apikey.html", context)
        else:
            context = {
                "api_key": "**********************************",
                "has_key": True,
            }
            return render(request, "accounts/apikey.html", context)


@unauthenticated_user
def subscription_inquiry(request):
    form = SubscriptionForm(request.POST or None)
    non_ror_institutes = serializers.serialize(
        "json", Institution.objects.filter(is_ror=False)
    )

    if request.method == "POST":
        """Begin reCAPTCHA validation"""
        recaptcha_response = request.POST.get("g-recaptcha-response")
        url = "https://www.google.com/recaptcha/api/siteverify"
        values = {
            "secret": settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            "response": recaptcha_response,
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        """ End reCAPTCHA validation """

        if (
            result["success"]
            and result.get("score", 0.0) >= settings.RECAPTCHA_REQUIRED_SCORE
            and form.is_valid()
        ):

            account_type_key = form.cleaned_data["account_type"]
            inquiry_type_key = form.cleaned_data["inquiry_type"]

            account_type_display = dict(
                form.fields["account_type"].choices
            ).get(account_type_key, "")
            inquiry_type_display = dict(
                form.fields["inquiry_type"].choices
            ).get(inquiry_type_key, "")
            form.cleaned_data["account_type"] = account_type_display
            form.cleaned_data["inquiry_type"] = inquiry_type_display

            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            organization = form.cleaned_data["organization_name"]

            if not last_name:
                form.cleaned_data["last_name"] = first_name
            account_exist = User.objects.filter(email=email).first()
            institution = Institution.objects.filter(
                institution_name=organization
            ).first()
            try:
                response = institute_account_subscription(
                    request,
                    institution,
                    account_exist,
                    form,
                    non_ror_institutes,
                )
                return response
            except Exception:
                messages.add_message(
                    request,
                    messages.ERROR,
                    (
                        "An unexpected error has occurred. Please"
                        "try contacting the Local Contexts HUB."
                    ),
                )
                return redirect("dashboard")
    return render(
        request,
        "accounts/subscription-inquiry.html",
        {
            "form": form,
            "non_ror_institutes": non_ror_institutes,
        },
    )
