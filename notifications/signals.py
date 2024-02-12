from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ActionNotification
from tklabels.models import TKLabel
from bclabels.models import BCLabel
from communities.models import JoinRequest
from projects.models import Project

@receiver(post_delete, sender=TKLabel)
def delete_related_notifications(sender, instance, **kwargs):
    ActionNotification.objects.filter(reference_id=str(instance.unique_id)).delete()

@receiver(post_delete, sender=BCLabel)
def delete_related_notifications(sender, instance, **kwargs):
    ActionNotification.objects.filter(reference_id=str(instance.unique_id)).delete()

@receiver(post_delete, sender=JoinRequest)
def delete_related_notifications(sender, instance, **kwargs):
    ActionNotification.objects.filter(reference_id=str(instance.id)).delete()