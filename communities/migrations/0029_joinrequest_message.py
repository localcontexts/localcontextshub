# Generated by Django 3.0.7 on 2021-06-21 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0028_auto_20210615_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='joinrequest',
            name='message',
            field=models.TextField(blank=True),
        ),
    ]
