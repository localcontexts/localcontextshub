# Generated by Django 3.0.7 on 2021-08-20 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0040_auto_20210819_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Discoverable', 'Discoverable'), ('Private', 'Private'), ('Public', 'Public')], max_length=20, null=True),
        ),
    ]
