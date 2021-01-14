from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from phone_field import PhoneField
from PIL import Image
from django.core.files.storage import default_storage
from io import BytesIO

from communities.models import Community
from institutions.models import Institution

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='photos/', blank=True, null=True, default='default.png')
    phone = PhoneField(blank=True, help_text='Contact phone number')
    nationality = models.CharField(verbose_name='nationality', max_length=60, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    city_or_town = models.CharField(verbose_name='city or town', max_length=80, blank=True, null=True)
    job_title = models.CharField(verbose_name='job title', max_length=80, blank=True, null=True)
    affiliation = models.CharField(verbose_name='affiliation', max_length=60, blank=True, null=True)
    community_member = models.BooleanField(default=False, null=True)
    is_researcher = models.BooleanField(default=False, null=True)

    def __str__(self):
        return str(self.user)
    
    # def save(self, *args, **kwargs):
    #     #run save of parent class above to save original image to disk
    #     super().save(*args, **kwargs)

    #     memfile = BytesIO()

    #     img = Image.open(self.profile_pic)
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size, Image.ANTIALIAS)
    #         img.save(memfile, 'PNG', quality=95)
    #         default_storage.save(self.profile_pic.name, memfile)
    #         memfile.close()
    #         img.close()

class UserInstitution(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    institutions = models.ManyToManyField(Institution, blank=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'User Institution'
        verbose_name_plural = 'User Institutions'

class UserCommunity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    communities = models.ManyToManyField(Community, blank=True, related_name="user_communities")

    @classmethod
    def create(cls, user):
        obj = cls(user=user)
        return obj

    def __str__(self):
        return str(self.user)
    
    class Meta:
        verbose_name = 'User Community'
        verbose_name_plural = 'User Communities'