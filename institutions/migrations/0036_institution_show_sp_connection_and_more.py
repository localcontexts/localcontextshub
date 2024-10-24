# Generated by Django 5.0.6 on 2024-08-23 16:32

import django.db.models.functions.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0035_remove_institution_is_submitted'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='show_sp_connection',
            field=models.BooleanField(default=True),
        ),
        migrations.AddConstraint(
            model_name='institution',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('institution_name'), name='institution_name', violation_error_message='This institution is already on the Hub.'),
        ),
    ]