# Generated by Django 3.0.7 on 2021-02-01 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0012_auto_20210201_2332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='target_species',
        ),
        migrations.AddField(
            model_name='project',
            name='recommended_citation',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
