# Generated by Django 5.0.6 on 2024-06-24 16:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_merge_20240507_0954'),
        ('serviceproviders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='service_provider',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscribed_service_provider', to='serviceproviders.serviceprovider'),
        ),
        migrations.AddField(
            model_name='useraffiliation',
            name='service_providers',
            field=models.ManyToManyField(blank=True, related_name='user_service_providers', to='serviceproviders.serviceprovider'),
        ),
    ]
