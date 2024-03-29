from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
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