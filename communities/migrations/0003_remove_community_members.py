# Generated by Django 3.0.7 on 2020-12-09 01:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0002_auto_20201209_0039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='community',
            name='members',
        ),
    ]
