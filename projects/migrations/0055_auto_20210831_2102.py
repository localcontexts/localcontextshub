# Generated by Django 3.0.7 on 2021-08-31 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0054_auto_20210830_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('Private', 'Private'), ('Discoverable', 'Discoverable')], max_length=20, null=True),
        ),
    ]
