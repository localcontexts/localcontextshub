# Generated by Django 5.0.6 on 2024-09-11 21:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('serviceproviders', '0004_alter_serviceprovider_show_connections'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceprovider',
            name='certified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_provider_approver', to=settings.AUTH_USER_MODEL),
        ),
    ]
