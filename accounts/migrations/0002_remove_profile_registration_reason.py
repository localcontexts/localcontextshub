# Generated by Django 3.0.7 on 2021-01-05 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='registration_reason',
        ),
    ]
