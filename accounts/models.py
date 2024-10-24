from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField
from django.utils import timezone
from django.core.exceptions import ValidationError

from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from serviceproviders.models import ServiceProvider


class Profile(models.Model):
    user = models.OneToOneField(
        User, null=True, on_delete=models.CASCADE, related_name="user_profile"
    )
    profile_pic = models.ImageField(
        upload_to='photos/', blank=True, null=True, default='default.png'
    )
    city_town = models.CharField(
        verbose_name='city or town', max_length=80, blank=True, null=True
    )
    state_province_region = models.CharField(
        verbose_name='state or province', max_length=100, blank=True, null=True
    )
    country = CountryField(blank=True, null=True)
    position = models.CharField(verbose_name='position', max_length=80, blank=True, null=True)
    affiliation = models.CharField(
        verbose_name='affiliation', max_length=250, blank=True, null=True
    )
    preferred_language = models.CharField(
        verbose_name='preferred language', max_length=80, blank=True, null=True
    )
    api_key = models.CharField(max_length=80, blank=True, null=True)
    languages_spoken = models.CharField(
        verbose_name='languages spoken', max_length=150, blank=True, null=True
    )
    is_researcher = models.BooleanField(default=False, null=True)
    onboarding_on = models.BooleanField(default=True, null=True, blank=True)

    def get_location(self):
        components = [self.city_town, self.state_province_region, self.country.name]
        location = ', '.join(filter(None, components)) or None
        return location

    def __str__(self):
        return str(self.user)

    class Meta:
        indexes = [models.Index(fields=["user"])]


class UserAffiliation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="user_affiliations"
    )
    communities = models.ManyToManyField(Community, blank=True, related_name="user_communities")
    institutions = models.ManyToManyField(
        Institution, blank=True, related_name="user_institutions"
    )
    service_providers = models.ManyToManyField(
        ServiceProvider, blank=True, related_name="user_service_providers"
    )

    @classmethod
    def create(cls, user):
        obj = cls(user=user)
        return obj

    def __str__(self):
        return str(self.user)

    class Meta:
        indexes = [models.Index(fields=["user"])]
        verbose_name = "User Affiliation"
        verbose_name_plural = "User Affiliations"


class SignUpInvitation(models.Model):
    email = models.EmailField(null=True)
    message = models.TextField(max_length=120, null=True, blank=True)
    sender = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE)
    date_sent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = "Sign Up Invitation"
        verbose_name_plural = "Sign Up Invitations"
        ordering = ("-date_sent",)


class Subscription(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('individual', 'Individual'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('cc_notice_only', 'CC Notice Only'),
        ('cc_notices', 'CC Notices'),
        ('member', 'Member'),
        ('service_provider', 'Service Provider'),
        ('founding_supporter', 'Founding Supporter')
    ]

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="subscribed_institution",
        blank=True,
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="subscribed_community",
        blank=True,
    )
    researcher = models.ForeignKey(
        Researcher,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="subscribed_researcher",
        blank=True,
    )
    service_provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="subscribed_service_provider",
        blank=True,
    )
    users_count = models.IntegerField(
        help_text="For unlimited counts the value shoud be -1"
    )
    api_key_count = models.IntegerField(
        help_text="For unlimited counts the value shoud be -1"
    )
    project_count = models.IntegerField(
        help_text="For unlimited counts the value shoud be -1"
    )
    notification_count = models.IntegerField(
        help_text="For unlimited counts the value shoud be -1"
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    date_last_updated = models.DateTimeField(auto_now=True)
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES)

    def clean(self):
        count = sum([
            bool(self.institution_id),
            bool(self.community_id),
            bool(self.researcher_id),
            bool(self.service_provider_id)
        ])
        if count != 1:
            errormsg = "Exactly one of institution, community, " \
                "researcher, service provider should be present."
            raise ValidationError(errormsg)

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # ordering = ('-date_sent', )


class InactiveUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    email = models.EmailField()
    date_joined = models.DateTimeField()

    def __str__(self):
        return self.username


class ServiceProviderConnections(models.Model):
    service_provider = models.ForeignKey(
        ServiceProvider, on_delete=models.CASCADE, default=None, null=True,
        related_name="service_provider_connection"
    )
    communities = models.ManyToManyField(
        Community, blank=True, related_name="service_provider_communities"
    )
    institutions = models.ManyToManyField(
        Institution, blank=True, related_name="service_provider_institutions"
    )
    researchers = models.ManyToManyField(
        Researcher, blank=True, related_name="service_provider_researchers"
    )

    def __str__(self):
        return str(self.service_provider)

    class Meta:
        indexes = [models.Index(fields=["service_provider"])]
        verbose_name = "Service Provider Connection"
        verbose_name_plural = "Service Provider Connections"
