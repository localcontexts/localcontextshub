# Generated by Django 3.1.13 on 2023-06-26 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0166_auto_20230626_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Contributor', 'Contributor'), ('Public', 'Public'), ('Private', 'Private')], max_length=20, null=True),
        ),
    ]
