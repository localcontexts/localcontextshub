# Generated by Django 3.1.13 on 2023-06-07 20:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0029_auto_20230525_2035'),
    ]

    operations = [
        migrations.RenameField(
            model_name='institution',
            old_name='institution_id',
            new_name='ror_id',
        ),
    ]
