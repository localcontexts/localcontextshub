# Generated by Django 3.1.14 on 2023-11-15 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0180_auto_20230818_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Contributor', 'Contributor'), ('Private', 'Private'), ('Public', 'Public')], max_length=20, null=True),
        ),
    ]