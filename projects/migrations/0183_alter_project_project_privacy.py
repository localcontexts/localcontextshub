# Generated by Django 3.2 on 2023-12-21 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0182_alter_project_project_privacy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Contributor', 'Contributor')], max_length=20, null=True),
        ),
    ]
