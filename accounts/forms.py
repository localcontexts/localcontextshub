from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from .models import Profile, SignUpInvitation
from helpers.emails import send_password_reset_email
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.exceptions import ValidationError


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, max_length=150, help_text="Required"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "w-100"}),
        }

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        # Cleans the data so nothing harmful can get passed though the form
        user.email = self.cleaned_data["email"]

        # if we want to save
        if commit:
            user.save()

        return user


class UserCreateProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["first_name", "last_name"]


# updating user instance (same as above but includes email)
class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "w-100"}),
            "first_name": forms.TextInput(attrs={"class": "w-100"}),
            "last_name": forms.TextInput(attrs={"class": "w-100"}),
        }

    def clean(self):
        super(UserUpdateForm, self).clean()
        email = self.cleaned_data.get("email")
        user_id = self.instance.id if self.instance else None
        if len(email) == 0:
            self._errors["email"] = self.error_class(["Email Is Required"])
        elif User.objects.filter(email=email).exclude(id=user_id).exists():
            self._errors["email"] = self.error_class(["Email already exists."])
        return self.cleaned_data


class ProfileCreationForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            "position",
            "affiliation",
            "city_town",
            "state_province_region",
            "country",
        ]
        widgets = {
            "position": forms.TextInput(attrs={"style": "width: 100%;"}),
            "affiliation": forms.TextInput(attrs={"class": "w-100"}),
            "city_town": forms.TextInput(attrs={"class": "w-100"}),
            "state_province_region": forms.TextInput(attrs={"class": "w-100"}),
        }


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            "position",
            "affiliation",
            "preferred_language",
            "languages_spoken",
            "city_town",
            "state_province_region",
            "country",
        ]
        widgets = {
            "position": forms.TextInput(attrs={"class": "w-100"}),
            "affiliation": forms.TextInput(attrs={"class": "w-100"}),
            "preferred_language": forms.TextInput(attrs={"class": "w-100"}),
            "languages_spoken": forms.TextInput(attrs={"class": "w-100"}),
            "city_town": forms.TextInput(attrs={"class": "w-100"}),
            "state_province_region": forms.TextInput(attrs={"class": "w-100"}),
        }


class ResendEmailActivationForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "w-100", "placeholder": "email@domain.com"}
        ),
    )


class SignUpInvitationForm(forms.ModelForm):

    class Meta:
        model = SignUpInvitation
        fields = ["email", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "cols": 65}),
            "email": forms.EmailInput(attrs={"size": 65}),
        }


class ContactOrganizationForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-100",
                "autocomplete": "off",
            }
        )
    )
    email = forms.EmailField(
        label=_("Email Address"),
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "w-100", "placeholder": "email@domain.com"}
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "cols": 65, "class": "w-100"})
    )


class CustomPasswordResetForm(PasswordResetForm):

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name=None,
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = User.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            send_password_reset_email(request, context)


class SubscriptionForm(forms.Form):
    ACCOUNT_TYPE_CHOICES = (
        ("", "Please select account type..."),
        ("institution_account", "Institution Account"),
        ("community_account", "Community Account"),
        ("researcher_account", "Researcher Account"),
    )
    INQUIRY_TYPE_CHOICES = (
        ("", "Please select inquiry type..."),
        ("subscriber", "Subscription"),
        ("member", "Membership"),
        ("service_provider", "Service Provider"),
        ("cc_only", "CC Notice Only"),
        ("something_else", " Something Else"),
        ("not_sure", "Not Sure"),
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-100",
                "autocomplete": "off",
            }
        )
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-100",
                "autocomplete": "off",
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "w-100",
                "autocomplete": "off",
            }
        )
    )
    account_type = forms.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "w-100",
                "autocomplete": "off",
                "placeholder": "Please select account type...",
            }
        ),
    )
    inquiry_type = forms.ChoiceField(
        choices=INQUIRY_TYPE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "w-100",
                "autocomplete": "off",
                "placeholder": "Please select inquiry type...",
            }
        ),
    )
    organization_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": "organizationInput",
                "class": "w-100",
                "autocomplete": "off",
            }
        )
    )

    def clean_account_type(self):
        account_type = self.cleaned_data.get("account_type")
        if not account_type:
            raise ValidationError("Please select an account type.")
        return account_type

    def clean_inquiry_type(self):
        inquiry_type = self.cleaned_data.get("inquiry_type")
        if not inquiry_type:
            raise ValidationError("Please select an inquiry type.")
        return inquiry_type
