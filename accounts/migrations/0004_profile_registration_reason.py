# Generated by Django 3.0.7 on 2020-11-12 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_profile_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='registration_reason',
            field=models.CharField(choices=[('', ''), ('community', 'Register a Community Account'), ('institution', 'Register an Institution Account'), ('research', 'Register a Research Account')], max_length=12, null=True),
        ),
    ]
