# Generated by Django 5.0.6 on 2024-07-09 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0062_noticedownloadtracker_service_provider'),
    ]

    operations = [
        migrations.AddField(
            model_name='hubactivity',
            name='service_provider_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
