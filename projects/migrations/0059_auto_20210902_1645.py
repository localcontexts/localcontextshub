# Generated by Django 3.0.7 on 2021-09-02 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0058_auto_20210901_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Discoverable', 'Discoverable'), ('Public', 'Public'), ('Private', 'Private')], max_length=20, null=True),
        ),
    ]
