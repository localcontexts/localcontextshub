# Generated by Django 3.0.7 on 2021-06-15 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0023_auto_20210615_1936'),
    ]

    operations = [
        migrations.RenameField(
            model_name='researcher',
            old_name='associated_institution',
            new_name='primary_institution',
        ),
    ]
