# Generated by Django 3.0.7 on 2021-08-19 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0033_auto_20210819_1235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='is_discoverable',
        ),
        migrations.RemoveField(
            model_name='project',
            name='is_public',
        ),
    ]
