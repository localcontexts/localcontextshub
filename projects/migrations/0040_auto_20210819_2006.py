# Generated by Django 3.0.7 on 2021-08-19 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0039_auto_20210819_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('Discoverable', 'Discoverable'), ('Private', 'Private')], max_length=20, null=True),
        ),
    ]
