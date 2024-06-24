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
    account_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=True, unique=True)
    contact_name = models.CharField(max_length=80, null=True, blank=True)
    contact_email = models.EmailField(max_length=254, null=True, blank=True)
    image = models.ImageField(upload_to=service_provider_img_path, blank=True, null=True)
    description = models.TextField(null=True, blank=True, validators=[MaxLengthValidator(200)])
    website = models.URLField(max_length=150, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    is_certified = models.BooleanField(default=False)

    # Managers
    objects = models.Manager()

    def __str__(self):
        return str(self.name)

    class Meta:
        indexes = [models.Index(fields=['id', 'account_creator', 'image'])]
        verbose_name = 'Service Provider'
        verbose_name_plural = 'Service Providers'
