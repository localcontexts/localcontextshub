# Generated by Django 3.1.13 on 2023-01-05 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0152_auto_20221221_2217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Discoverable', 'Discoverable')], max_length=20, null=True),
        ),
    ]
