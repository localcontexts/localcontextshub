from datetime import datetime, timezone

from django.db.models.signals import post_save, post_delete, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver

from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from .models import Profile, UserAffiliation, InactiveUser


# When a user is saved, send this signal
# (Create User Profile and Affiliation instances)
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        UserAffiliation.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.user_profile.save()


@receiver(post_delete, sender=InactiveUser)
def delete_related_user(sender, instance, **kwargs):
    instance.user.delete()


@receiver(pre_delete, sender=User)
def log_delete_user(sender, instance, **kwargs):
    """
    Logs deleted user data for debugging purposes
    """

    data = {
        'UTC-TIME': datetime.now(timezone.utc),
        'RELATED-RESEARCHER': None,
        'RELATED-COMMUNITIES': [],
        'RELATED-INSTITUTIONS': [],
    }

    # get related researcher data of interest for this user
    if Researcher.objects.filter(user=instance).exists():
        researcher = Researcher.objects.get(user=instance)
        data['RELATED-RESEARCHER'] = {
            'id': researcher.id,
            'orcid': researcher.orcid,
            'contact_email': researcher.contact_email,
        }

    # get related community data of interest for this user
    for community in Community.objects.filter(user=instance):
        data['RELATED-COMMUNITIES'].append(
            {
                'id': community.id,
                'community_name': community.community_name,
                'contact_email': community.contact_email,
                'is_approved': community.is_approved,

            }
        )

    # get related institution data of interest for this user
    for institution in Institution.objects.filter(user=instance):
        data['RELATED-INSTITUTIONS'].append(
            {
                'id': institution.id,
                'institution_name': institution.community_name,
                'institution_email': institution.contact_email,
                'is_approved': institution.is_approved,

            }
        )

    print(data)
