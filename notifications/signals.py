from django.db.models.signals import post_delete
from django.dispatch import receiver

from bclabels.models import BCLabel
from communities.models import JoinRequest
from projects.models import Project
from tklabels.models import TKLabel

from .models import ActionNotification


@receiver(post_delete, sender=TKLabel)
@receiver(post_delete, sender=BCLabel)
@receiver(post_delete, sender=Project)
@receiver(post_delete, sender=JoinRequest)
def delete_related_notifications(sender, instance, **kwargs):
    if sender in [TKLabel, BCLabel, Project]:
        ActionNotification.objects.filter(reference_id=str(instance.unique_id)).delete()
    elif sender == JoinRequest:
        ActionNotification.objects.filter(reference_id=str(instance.id)).delete()
