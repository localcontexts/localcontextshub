# Generated by Django 3.0.7 on 2021-01-18 23:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0004_delete_userinstitution'),
        ('researchers', '0004_auto_20210118_2306'),
        ('bclabels', '0014_auto_20210118_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bcnotice',
            name='placed_by_institution',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='institutions.Institution'),
        ),
        migrations.AlterField(
            model_name='bcnotice',
            name='placed_by_researcher',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='researchers.Researcher'),
        ),
    ]
