# Generated by Django 3.0.7 on 2020-12-23 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0005_auto_20201222_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotification',
            name='reference_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
