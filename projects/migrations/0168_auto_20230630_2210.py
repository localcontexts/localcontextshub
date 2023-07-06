# Generated by Django 3.1.13 on 2023-06-30 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0167_auto_20230626_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('Contributor', 'Contributor'), ('Private', 'Private')], max_length=20, null=True),
        ),
    ]
