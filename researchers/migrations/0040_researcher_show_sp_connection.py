# Generated by Django 5.0.6 on 2024-08-23 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0039_remove_researcher_is_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='researcher',
            name='show_sp_connection',
            field=models.BooleanField(default=True),
        ),
    ]
