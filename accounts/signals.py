import pprint

from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from helpers.logging import get_log_data

from .models import InactiveUser, Profile, UserAffiliation


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
    log_data = get_log_data(instance)
    pprint.pprint(log_data)
