# Generated by Django 3.0.7 on 2020-12-18 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20201218_2241'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usernotification',
            options={'verbose_name': 'Notification', 'verbose_name_plural': 'Notifications'},
        ),
    ]
