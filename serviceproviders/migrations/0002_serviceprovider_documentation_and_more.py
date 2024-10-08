# Generated by Django 5.0.6 on 2024-07-08 20:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('serviceproviders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceprovider',
            name='documentation',
            field=models.URLField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='editors',
            field=models.ManyToManyField(blank=True, related_name='service_provider_editors', to=settings.AUTH_USER_MODEL),
        ),
    ]