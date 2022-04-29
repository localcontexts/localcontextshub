# Generated by Django 3.1.13 on 2022-04-29 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0104_auto_20220428_2319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Discoverable', 'Discoverable'), ('Private', 'Private'), ('Public', 'Public')], max_length=20, null=True),
        ),
    ]
