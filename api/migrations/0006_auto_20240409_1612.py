# Generated by Django 3.2 on 2024-04-09 20:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0050_merge_0048_auto_20240123_0046_0049_alter_boundary_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('institutions', '0032_institution_is_subscribed'),
        ('researchers', '0036_alter_researcher_id'),
        ('api', '0005_auto_20240409_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountapikey',
            name='community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='community_api_keys', to='communities.community'),
        ),
        migrations.AlterField(
            model_name='accountapikey',
            name='developer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_api_keys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='accountapikey',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='institution_api_keys', to='institutions.institution'),
        ),
        migrations.AlterField(
            model_name='accountapikey',
            name='researcher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='researcher_api_keys', to='researchers.researcher'),
        ),
    ]
