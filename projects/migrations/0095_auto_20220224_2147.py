# Generated by Django 3.1.13 on 2022-02-24 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0094_auto_20220221_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Discoverable', 'Discoverable'), ('Private', 'Private'), ('Public', 'Public')], max_length=20, null=True),
        ),
    ]
