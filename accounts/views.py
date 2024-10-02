# Captcha validation imports
import urllib
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.views import ConnectionsView, SignupView

# For emails
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import (PasswordChangeForm, PasswordResetView, SetPasswordForm)
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View
from unidecode import unidecode

from helpers.emails import (
    add_to_newsletter_mailing_list, generate_token, get_newsletter_member_info,
    resend_activation_email, send_activation_email, send_email_verification,
    send_invite_user_email, send_welcome_email, unsubscribe_from_mailing_list,
    add_to_active_users_mailing_list, remove_from_active_users_mailing_list
)

from .forms import (
    RegistrationForm, ResendEmailActivationForm, CustomPasswordResetForm, UserCreateProfileForm,
    ProfileCreationForm, UserUpdateForm, ProfileUpdateForm, SignUpInvitationForm,
    SubscriptionForm,
)

from .utils import (
    get_next_path, get_users_name, return_registry_accounts, manage_mailing_list,
    institute_account_subscription, escape_single_quotes, determine_user_role,
    remove_user_from_account
)
from institutions.utils import get_institution
from localcontexts.utils import dev_prod_or_local
from researchers.utils import is_user_researcher
from helpers.utils import (
    accept_member_invite, validate_email, validate_recaptcha, check_member_role
)
from .models import SignUpInvitation, Profile, UserAffiliation, Subscription
from helpers.models import HubActivity
from projects.models import Project
from communities.models import InviteMember, Community
from institutions.models import Institution
from researchers.models import Researcher
from serviceproviders.models import ServiceProvider

from .decorators import unauthenticated_user
from maintenance_mode.decorators import force_maintenance_mode_off


@unauthenticated_user
def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            if validate_recaptcha(request):
                user = form.save(commit=False)

                if User.objects.filter(email=user.email).exists():
                    messages.error(request, 'A user with this email already exists.')
                    return redirect('register')
                elif User.objects.filter(username__iexact=user.username.lower()).exists():
                    messages.error(request, 'A user with this username already exists.')
                    return redirect('register')
                elif not validate_email(email=user.email):
                    messages.error(request, "The email you entered is invalid")
                    return redirect("register")
                else:
                    user.is_active = False
                    user.save()

                    # If SignupInvite instances exist, delete them
                    if SignUpInvitation.objects.filter(email=user.email).exists():
                        for invite in SignUpInvitation.objects.filter(email=user.email):
                            invite.delete()

                    send_activation_email(request, user)
                    HubActivity.objects.create(action_user_id=user.id, action_type="New User")
                    return redirect('verify')
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

            add_to_active_users_mailing_list(request, user.email, None)

            messages.add_message(
                request, messages.INFO,
                'Profile activation successful. You are now able to login.'
            )
            return redirect('login')
        return render(request, 'snippets/activate-failed.html', status=401)


@unauthenticated_user
def verify(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect("/dashboard")

    form = ResendEmailActivationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            active_users = User._default_manager.filter(
                **{
                    '%s__iexact' % User.get_email_field_name(): form.cleaned_data['email'],
                    'is_active': False,
                }
            )

            if active_users:
                resend_activation_email(request, active_users)
                messages.add_message(request, messages.INFO, 'Activation email sent!')
                return redirect('verify')
            else:
                messages.add_message(
                    request, messages.ERROR, 'Email did not match any registration email.'
                )
                return redirect('verify')
    return render(request, 'accounts/verify.html', {'form': form})


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
                        request, user, backend='django.contrib.auth.backends.ModelBackend'
                    )
                    # Welcome email
                    send_welcome_email(request, user)
                    return redirect("create-profile")
                else:
                    auth.login(
                        request, user, backend='django.contrib.auth.backends.ModelBackend'
                    )
                    return redirect(get_next_path(request, default_path='dashboard'))
            else:
                if not user.last_login:
                    messages.error(
                        request, 'Your account is not active yet. '
                        'Please verify your email.'
                    )
                    if SignUpInvitation.objects.filter(email=user.email).exists():
                        for invite in SignUpInvitation.objects.filter(email=user.email):
                            invite.delete()

                    send_activation_email(request, user)
                    return redirect("verify")
                else:
                    messages.error(
                        request, 'Your account is not active. '
                        'Please contact support@localcontexts.org.'
                    )
                    return redirect('login')
        else:
            messages.error(request, 'Your username or password does not match an account.')
            return redirect('login')
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
                "Google once you login."
            )
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class CustomSocialConnectionsView(ConnectionsView):

    def dispatch(self, request, *args, **kwargs):
        provider = kwargs['provider']
        social_account = SocialAccount.objects.filter(provider=provider,
                                                      user=request.user).first()
        has_password = request.user.has_usable_password()
        if social_account and has_password:
            social_account.delete()
            messages.info(request, "The social account has been disconnected.")
            return redirect("link-account")
        else:
            messages.error(request, 'Please set password first to unlink an account.')
            return redirect('link-account')
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

    affiliation = user.user_affiliations.prefetch_related(
        'communities', 'institutions', 'service_providers', 'communities__admins',
        'communities__editors', 'communities__viewers', 'institutions__admins',
        'institutions__editors', 'institutions__viewers'
    ).all().first()

    user_communities = affiliation.communities.all()
    user_institutions = affiliation.institutions.all()
    user_service_providers = affiliation.service_providers.all()
    unsubscribed_institute = Institution.objects.filter(
        institution_creator=user
    ).first()

    if request.method == "POST":
        profile.onboarding_on = False
        profile.save()

    context = {
        "profile": profile,
        "user_communities": user_communities,
        "user_institutions": user_institutions,
        "user_service_providers": user_service_providers,
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
        profile_form = ProfileCreationForm(request.POST, instance=request.user.user_profile)
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
        new_email = user_form.data['email']

        if new_email != old_email and new_email != "" and user_form.is_valid():
            user_form.instance.email = old_email
            profile_form.save()
            user_form.save()
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(request.user)
            encoded_token = urlsafe_base64_encode(
                force_bytes(f"{token} {new_email} {request.user.id}")
            )
            verification_url = f"http://{get_current_site(request).domain}" \
                               f"/confirm-email/{request.user.pk}" \
                               f"/{encoded_token}"
            send_email_verification(request, old_email, new_email, verification_url)
            messages.add_message(
                request, messages.INFO, f'A verification email has been sent to {new_email}.'
            )
            return redirect('update-profile')
        elif user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            return redirect("update-profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.user_profile)

    context = {'profile': profile, 'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'accounts/update-profile.html', context)


@login_required(login_url="login")
def confirm_email(request, uidb64, token):
    try:
        decoded_token = urlsafe_base64_decode(token).decode("utf-8")
        new_token, new_email, user_id_str = decoded_token.split(" ")
    except ValueError:
        messages.add_message(request, messages.ERROR, 'Invalid Verification token.')
        return redirect('login')
    new_token = new_token.strip()
    new_email = new_email.strip()
    user_id = user_id_str.strip()

    if not User.objects.filter(pk=user_id).exists():
        messages.add_message(request, messages.ERROR, "User not found.")
        return redirect("login")
    user = User.objects.get(pk=user_id)
    user.email = new_email
    user.save()
    messages.add_message(request, messages.SUCCESS, 'Email updated Successfully.')
    return redirect('dashboard')


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
            messages.add_message(request, messages.SUCCESS, 'Password successfully changed!')
            return redirect('change-password')
        else:
            messages.add_message(request, messages.ERROR, 'Something went wrong.')
            return redirect('change-password')
    return render(request, 'accounts/change-password.html', {'profile': profile, 'form': form})


@login_required(login_url="login")
def deactivate_user(request):
    profile = Profile.objects.select_related("user").get(user=request.user)
    user = request.user
    user_role = determine_user_role(user=user)
    profile = Profile.objects.select_related('user').get(user=user)
    affiliations = UserAffiliation.objects.prefetch_related(
        'communities', 'institutions', 'communities__community_creator',
        'institutions__institution_creator'
    ).get(user=user)
    users_name = get_users_name(user)
    researcher = Researcher.objects.filter(user=user).first()

    if request.method == "POST":
        if user_role != 'is_creator_or_project_creator':

            # removes user from their community and institution accounts
            remove_user_from_account(user)
            # update active user mailing list with name
            remove_from_active_users_mailing_list(request, user.email, user.get_full_name())

            user.is_active = False
            user.save()
            auth.logout(request)
            messages.add_message(
                request, messages.INFO, 'Your account has been deactivated. '
                'If this was a mistake please contact support@localcontexts.org.'
            )
            return redirect('login')

    return render(request, 'accounts/deactivate.html', {
        'profile': profile,
        'user_role': user_role,
        'affiliations': affiliations,
        'researcher': researcher,
        'users_name': users_name
    })


@login_required(login_url="login")
def manage_organizations(request):
    profile = Profile.objects.select_related("user").get(user=request.user)
    affiliations = UserAffiliation.objects.prefetch_related(
        'communities', 'institutions', 'service_providers', 'communities__community_creator',
        'institutions__institution_creator', 'service_providers__account_creator',
    ).get(user=request.user)
    researcher = Researcher.objects.none()
    users_name = get_users_name(request.user)
    if Researcher.objects.filter(user=request.user).exists():
        researcher = Researcher.objects.get(user=request.user)
    return render(
        request, 'accounts/manage-orgs.html', {
            'profile': profile,
            'affiliations': affiliations,
            'researcher': researcher,
            'users_name': users_name
        }
    )


@login_required(login_url='login')
def leave_account(request, account_type, account_id):
    # Define a dictionary to map account types to their respective models
    account_models = {
        "institution": Institution,
        "community": Community,
    }

    # Get the model class based on the account_type or return a 404 if not found
    model = account_models.get(account_type)
    account = get_object_or_404(model, id=account_id) if model else None

    if account:
        # Check if the user holds a role in the account
        if (request.user in account.admins.all() or
                request.user in account.editors.all() or
                request.user in account.viewers.all()):

            remove_user_from_account(request.user, account)
        else:
            # Return a 403 Forbidden response if the user does not hold a role in the account
            return HttpResponseForbidden("You do not have permission to perform this action.")

    return redirect('manage-orgs')


@login_required(login_url="login")
def link_account(request):
    has_social_account = SocialAccount.objects.filter(user=request.user).exists()
    provider = None
    if has_social_account:
        social_account = SocialAccount.objects.filter(user=request.user).first()
        provider = social_account.provider

    return render(
        request, 'accounts/link-account.html', {
            'socialaccount': has_social_account,
            'provider': provider
        }
    )


@login_required(login_url="login")
def member_invitations(request):
    profile = Profile.objects.select_related("user").get(user=request.user)
    member_invites = InviteMember.objects.filter(receiver=request.user)
    for invite in member_invites:
        if invite.institution and invite.role.lower() in (
            "editor",
            "administrator",
            "admin",
        ):
            try:
                subscription = Subscription.objects.get(
                    institution=invite.institution_id
                )
                invite.has_zero_user_count = subscription.users_count == 0
            except Subscription.DoesNotExist:
                subscription = None

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
                messages.add_message(request, messages.ERROR, 'This user is already in the Hub.')
                return redirect(selected_path)
            else:
                if SignUpInvitation.objects.filter(email=data.email).exists():
                    messages.add_message(
                        request, messages.ERROR,
                        'An invitation has already been sent to this email.'
                    )
                    return redirect(selected_path)
                else:
                    messages.add_message(request, messages.SUCCESS, 'Invitation sent!')
                    send_invite_user_email(request, data)
                    data.save()
                    return redirect(selected_path)

    # when validation fails and selected_path is not the default
    # redirect to selected path
    if selected_path.strip("/") != default_path:
        return redirect(selected_path)

    return render(request, 'accounts/invite.html',
                  {'invite_form': invite_form})


def registry(request, filtertype=None):
    default_items_per_page = 20
    try:
        c = Community.objects.select_related('community_creator').prefetch_related(
            'admins', 'editors', 'viewers'
        ).all().order_by('community_name')
        i = Institution.objects.select_related('institution_creator').prefetch_related(
            'admins', 'editors', 'viewers'
        ).all().order_by('institution_name')
        r = Researcher.objects.select_related('user').all().order_by('user__username')
        sp = (ServiceProvider.objects.select_related("account_creator").all().order_by("name"))

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
            sp = sp.filter(name__unaccent__icontains=q)
            r = r.filter(
                Q(user__username__unaccent__icontains=q)
                | Q(user__first_name__unaccent__icontains=q)
                | Q(user__last_name__unaccent__icontains=q)
            )

            cards = return_registry_accounts(c, r, i, sp)

            p = Paginator(cards, default_items_per_page)

        else:
            if filtertype == "community-all":
                cards = c
            elif filtertype == "community-members":
                cards = c.filter(is_approved=True)
            elif filtertype == "institution-all":
                cards = i
            elif filtertype == "institution-subscribed":
                cards = i.filter(is_subscribed=True)
            elif filtertype == "service-provider-all":
                cards = sp
            elif filtertype == "service-provider-certified":
                cards = sp.filter(is_certified=True)
            elif filtertype == "researcher-all":
                cards = r
            elif filtertype == "researcher-subscribed":
                cards = r.filter(is_subscribed=True)
            elif filtertype == 'engagement-notice':
                researchers_with_otc = r.filter(otc_researcher_url__isnull=False).distinct()
                institutions_with_otc = i.filter(otc_institution_url__isnull=False).distinct()
                service_providers_with_otc = sp.filter(
                    otc_service_provider_url__isnull=False).distinct()
                cards = return_registry_accounts(
                    None,
                    researchers_with_otc,
                    institutions_with_otc,
                    service_providers_with_otc
                )
            elif filtertype == 'all':
                return redirect('registry')
            else:
                cards = return_registry_accounts(c, r, i, sp)

            p = Paginator(cards, default_items_per_page)

        page_num = request.GET.get("page", 1)
        page = p.page(page_num)

        context = {
            "researchers": r,
            "communities": c,
            "institutions": i,
            "service_providers": sp,
            "items": page,
            "filtertype": filtertype,
        }

        return render(request, "accounts/registry.html", context)

    except Exception:
        raise Http404()


def projects_board(request, filtertype=None):
    try:
        institutions = Institution.objects.all()
        approved_communities = Community.objects.filter(is_approved=True
                                                        ).values_list('id', flat=True)

        public_projects_filter = Q(project_privacy='Public')
        institution_projects_filter = Q(
            project_creator_project__institution__in=institutions
        )
        community_projects_filter = Q(
            project_creator_project__community__in=approved_communities
        )
        researcher_projects_filter = Q(
            project_creator_project__researcher__user__isnull=False,
            project_creator_project__researcher__is_subscribed=True
        )
        projects = (
            Project.objects.filter(public_projects_filter & (
                    institution_projects_filter | community_projects_filter
                    | researcher_projects_filter
                )
            ).select_related("project_creator").order_by("-date_modified")
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
                ).distinct()
            elif filtertype == 'notices':
                results = projects.filter(project_notice__archived=False).distinct()
            else:
                results = projects

            p = Paginator(results, 10)

        page_num = request.GET.get("page", 1)
        page = p.page(page_num)

        context = {'projects': projects, 'items': page, 'filtertype': filtertype}
        return render(request, 'accounts/projects-board.html', context)
    except Exception:
        raise Http404()


# Hub stats page
def hub_counter(request):
    return redirect("/admin/dashboard/")


@force_maintenance_mode_off
def newsletter_subscription(request):
    environment = dev_prod_or_local(request.get_host())

    if environment == 'PROD' or 'localhost' in request.get_host():
        if request.method == 'POST':
            if 'topic' not in request.POST:
                messages.add_message(
                    request, messages.ERROR, 'Please select at least one topic.'
                )
                return redirect('newsletter-subscription')
            else:
                if validate_recaptcha(request):
                    first_name = request.POST["first_name"]
                    last_name = request.POST["last_name"]
                    name = str(first_name) + str(" ") + str(last_name)
                    email = request.POST["email"]
                    emailb64 = urlsafe_base64_encode(force_bytes(email))
                    variables = manage_mailing_list(request, first_name, emailb64)
                    add_to_newsletter_mailing_list(str(email), str(name), str(variables))
                    message_text = mark_safe(
                        'Thank&nbsp;you&nbsp;an&nbsp;'
                        'email&nbsp;has&nbsp;been&nbsp;sent'
                    )
                    messages.add_message(request, messages.SUCCESS, message_text)
                    return render(
                        request, 'accounts/newsletter-subscription.html', {'emailb64': emailb64}
                    )
                else:
                    messages.error(request, 'Invalid reCAPTCHA. Please try again.')

        return render(request, "accounts/newsletter-subscription.html")
    else:
        return redirect("login")


@force_maintenance_mode_off
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
                            request, messages.SUCCESS, 'You unsubscribed successfully!'
                        )
                        return redirect('newsletter-unsubscription', emailb64=emailb64)
                    elif 'topic' in request.POST:
                        variables = manage_mailing_list(request, first_name, email)
                        add_to_newsletter_mailing_list(str(email), str(name), str(variables))
                        messages.add_message(
                            request, messages.SUCCESS, 'Your preferences have been updated!'
                        )
                        return redirect('newsletter-unsubscription', emailb64=emailb64)
                    else:
                        messages.add_message(
                            request, messages.ERROR, 'Please select at least one option.'
                        )
                        return redirect('newsletter-unsubscription', emailb64=emailb64)
            return render(request, 'accounts/newsletter-unsubscription.html', context)
        except Exception:
            raise Http404()

    else:
        return redirect("login")


def subscription_inquiry(request):
    form = SubscriptionForm(request.POST or None)
    form.fields.pop('account_type', None)
    non_ror_institutes = serializers.serialize(
        "json", Institution.objects.filter(is_ror=False)
    )
    communities = serializers.serialize("json", Community.approved.all())
    service_providers = serializers.serialize("json", ServiceProvider.certified.all())

    non_ror_institutes = escape_single_quotes(non_ror_institutes)
    communities = escape_single_quotes(communities)
    service_providers = escape_single_quotes(service_providers)

    if request.method == "POST":
        if validate_recaptcha(request) and form.is_valid():
            inquiry_type_key = form.cleaned_data["inquiry_type"]
            inquiry_type_display = dict(form.fields["inquiry_type"].choices
                                        ).get(inquiry_type_key, "")
            form.cleaned_data["inquiry_type"] = inquiry_type_display

            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            organization = form.cleaned_data["organization_name"]

            if not last_name:
                form.cleaned_data["last_name"] = first_name
            account_exist = User.objects.filter(email=email).first()
            institution = Institution.objects.filter(institution_name=organization).first()
            try:
                response = institute_account_subscription(
                    request, institution, account_exist, form, non_ror_institutes,
                )
                return response
            except Exception:
                messages.add_message(
                    request, messages.ERROR,
                    (
                        "An unexpected error has occurred. Please "
                        "try contacting the Local Contexts HUB."
                    ),
                )
                return redirect("dashboard")
    return render(
        request, "accounts/subscription-inquiry.html",
        {
            "form": form,
            "non_ror_institutes": non_ror_institutes,
            "communities": communities,
            "service_providers": service_providers,
        },
    )


@login_required(login_url="login")
def subscription(request, pk, account_type, related=None):
    if dev_prod_or_local(request.get_host()) == "SANDBOX":
        return redirect("dashboard")

    renew = False

    if account_type == 'institution' and (
        request.user in get_institution(pk).get_admins()
        or
        request.user == get_institution(pk).institution_creator
    ):
        institution = get_institution(pk)
        member_role = check_member_role(request.user, institution)
        try:
            subscription = Subscription.objects.get(institution=institution)
        except Subscription.DoesNotExist:
            subscription = None
        if subscription is not None:
            if subscription.end_date and subscription.end_date < timezone.now():
                renew = True
        context = {
            "institution": institution,
            "subscription": subscription,
            "start_date": subscription.start_date.strftime('%d %B %Y')
            if subscription and subscription.start_date is not None
            else None,
            "end_date": subscription.end_date.strftime('%d %B %Y')
            if subscription and subscription.end_date is not None
            else None,
            "renew": renew,
            "member_role": member_role,
        }
    if account_type == 'researcher':
        researcher = Researcher.objects.get(id=pk)
        if researcher.is_subscribed:
            subscription = Subscription.objects.filter(researcher=researcher).first()
        else:
            subscription = None
        if subscription is not None:
            if subscription.end_date and subscription.end_date < timezone.now():
                renew = True
        context = {
            "researcher": researcher,
            "subscription": subscription,
            "start_date": subscription.start_date.strftime('%d %B %Y')
            if subscription and subscription.start_date is not None
            else None,
            "end_date": subscription.end_date.strftime('%d %B %Y')
            if subscription and subscription.end_date is not None
            else None,
            "renew": renew
        }
    return render(
        request, 'account_settings_pages/_subscription.html',
        context
    )
