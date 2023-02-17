# Generated by Django 3.1.13 on 2022-10-21 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0145_auto_20220930_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Discoverable', 'Discoverable'), ('Public', 'Public')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='projectnote',
            name='note',
            field=models.TextField(blank=True, null=True, verbose_name='Community Note'),
        ),
    ]