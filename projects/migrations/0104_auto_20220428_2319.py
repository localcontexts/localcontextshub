# Generated by Django 3.1.13 on 2022-04-28 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0103_auto_20220413_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Discoverable', 'Discoverable'), ('Public', 'Public'), ('Private', 'Private')], max_length=20, null=True),
        ),
    ]
