# Generated by Django 3.2 on 2024-04-10 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20240409_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountapikey',
            name='encrypted_key',
            field=models.CharField(editable=False, max_length=255, unique=True),
        ),
    ]
