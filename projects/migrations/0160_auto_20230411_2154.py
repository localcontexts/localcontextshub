# Generated by Django 3.1.13 on 2023-04-11 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0159_auto_20230331_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('Private', 'Private'), ('Contributor', 'Contributor')], max_length=20, null=True),
        ),
    ]
