# Generated by Django 3.1.13 on 2021-12-04 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0086_auto_20211202_2312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Discoverable', 'Discoverable')], max_length=20, null=True),
        ),
    ]
