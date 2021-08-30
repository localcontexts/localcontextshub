# Generated by Django 3.0.7 on 2021-08-30 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0051_auto_20210826_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Discoverable', 'Discoverable'), ('Public', 'Public')], max_length=20, null=True),
        ),
    ]
