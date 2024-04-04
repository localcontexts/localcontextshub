# Generated by Django 4.2.11 on 2024-03-22 11:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0020_subscription"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="date_last_updated",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="subscription",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="subscription",
            name="start_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
