# Generated by Django 3.0.7 on 2021-06-17 21:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0032_auto_20210617_2127'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='actionnotification',
            options={'ordering': ('viewed', '-created'), 'verbose_name': 'Action Notification', 'verbose_name_plural': 'Action Notifications'},
        ),
        migrations.AlterModelOptions(
            name='usernotification',
            options={'ordering': ('viewed', '-created'), 'verbose_name': 'User Notification', 'verbose_name_plural': 'User Notifications'},
        ),
    ]
