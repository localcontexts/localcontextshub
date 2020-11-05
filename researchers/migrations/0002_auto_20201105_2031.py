# Generated by Django 3.0.7 on 2020-11-05 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='researcher',
            name='orcid',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='researcher',
            name='project',
            field=models.ManyToManyField(blank=True, to='researchers.Project'),
        ),
    ]
