# Generated by Django 3.1.13 on 2022-02-21 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bclabels', '0042_bclabel_audiofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='bclabel',
            name='svg_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
