# Generated by Django 3.1.13 on 2022-07-01 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0022_auto_20220629_2128'),
    ]

    operations = [
        migrations.AddField(
            model_name='opentocollaboratenoticeurl',
            name='added',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
