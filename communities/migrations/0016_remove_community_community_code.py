# Generated by Django 3.0.7 on 2021-03-18 18:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0015_auto_20210201_2119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='community',
            name='community_code',
        ),
    ]
