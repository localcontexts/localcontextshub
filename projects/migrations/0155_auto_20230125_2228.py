# Generated by Django 3.1.13 on 2023-01-25 22:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0154_auto_20230119_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectnote',
            name='sender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_note_sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Discoverable', 'Discoverable')], max_length=20, null=True),
        ),
    ]
