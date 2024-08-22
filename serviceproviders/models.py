from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
import uuid
import os

def service_provider_img_path(self, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid.uuid4()), ext)
    return os.path.join('users/service-provider-images', filename)

class ServiceProvider(models.Model):
    account_creator = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True
    )
    name = models.CharField(max_length=100, null=True, unique=True)
    contact_name = models.CharField(max_length=80, null=True, blank=True)
    contact_email = models.EmailField(max_length=254, null=True, blank=True)
    image = models.ImageField(
        upload_to=service_provider_img_path, blank=True, null=True
    )
    description = models.TextField(
        null=True, blank=True, validators=[MaxLengthValidator(200)]
    )
    website = models.URLField(max_length=150, blank=True, null=True)
    documentation = models.URLField(max_length=150, blank=True, null=True)
    editors = models.ManyToManyField(
        User, blank=True, related_name="service_provider_editors"
    )
    created = models.DateTimeField(auto_now_add=True, null=True)
    is_certified = models.BooleanField(default=False)
    show_connections = models.BooleanField(default=True)

    # Managers
    objects = models.Manager()

    def __str__(self):
        return str(self.name)

    def get_member_count(self):
        admins = 1
        editors = self.editors.count()
        total_members = admins + editors
        return total_members

    def get_editors(self):
        return self.editors.all()

    def is_user_in_service_provider(self, user):
        if user in self.editors.all() or user == self.account_creator:
            return True
        else:
            return False

    class Meta:
        indexes = [models.Index(fields=['id', 'account_creator', 'image'])]
        verbose_name = 'Service Provider'
        verbose_name_plural = 'Service Providers'
