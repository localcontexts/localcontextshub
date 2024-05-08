# Generated by Django 3.2 on 2024-04-08 16:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('communities', '0050_merge_0048_auto_20240123_0046_0049_alter_boundary_id'),
        ('institutions', '0032_institution_is_subscribed'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountAPIKey',
            fields=[
                ('id', models.CharField(editable=False, max_length=150, primary_key=True, serialize=False, unique=True)),
                ('prefix', models.CharField(editable=False, max_length=8, unique=True)),
                ('hashed_key', models.CharField(editable=False, max_length=150)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('name', models.CharField(default=None, help_text='A free-form name for the API key. Need not be unique. 50 characters max.', max_length=50)),
                ('revoked', models.BooleanField(blank=True, default=False, help_text='If the API key is revoked, clients cannot use it anymore. (This cannot be undone.)')),
                ('expiry_date', models.DateTimeField(blank=True, help_text='Once API key expires, clients cannot use it anymore.', null=True, verbose_name='Expires')),
                ('communities', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_api_keys', to='communities.community')),
                ('developers', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_api_keys', to=settings.AUTH_USER_MODEL)),
                ('institutions', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='institution_api_keys', to='institutions.institution')),
            ],
            options={
                'verbose_name': 'Account API Key',
                'verbose_name_plural': 'Account API Keys',
                'ordering': ('-created',),
                'abstract': False,
            },
        ),
    ]