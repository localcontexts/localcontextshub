# Generated by Django 3.1.13 on 2022-04-13 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0102_auto_20220405_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Discoverable', 'Discoverable'), ('Public', 'Public')], max_length=20, null=True),
        ),
    ]
