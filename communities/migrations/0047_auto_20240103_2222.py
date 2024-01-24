# Generated by Django 3.1.14 on 2024-01-03 22:22

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0046_auto_20240103_2039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boundary',
            name='coordinates',
        ),
        migrations.AddField(
            model_name='boundary',
            name='coordinates',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True), blank=True, null=True, size=2), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='community',
            name='source_of_boundaries',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.DeleteModel(
            name='Coordinate',
        ),
    ]