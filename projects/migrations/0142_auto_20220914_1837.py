# Generated by Django 3.1.13 on 2022-09-14 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0141_auto_20220909_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Discoverable', 'Discoverable'), ('Public', 'Public')], max_length=20, null=True),
        ),
    ]
