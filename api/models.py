from django.db import models
from rest_framework_api_key.models import AbstractAPIKey

from django.contrib.auth.models import User
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher

class AccountAPIKey(AbstractAPIKey):
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="institution_api_keys"
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="community_api_keys"
    )
    researcher = models.ForeignKey(
        Researcher,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="researcher_api_keys"
    )
    developer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="user_api_keys"
    )
    encrypted_key = models.CharField(unique=True, max_length=255, null=True, blank=True)

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "Account API Key"
        verbose_name_plural = "Account API Keys"