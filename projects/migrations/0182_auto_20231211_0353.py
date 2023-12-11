# Generated by Django 3.1.14 on 2023-12-11 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0181_auto_20231127_0435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Contributor', 'Contributor'), ('Public', 'Public'), ('Private', 'Private')], max_length=20, null=True),
        ),
    ]
