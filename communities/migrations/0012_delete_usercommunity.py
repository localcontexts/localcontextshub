# Generated by Django 3.0.7 on 2021-01-14 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0011_invitemember_message'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserCommunity',
        ),
    ]
