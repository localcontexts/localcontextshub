# Generated by Django 3.1.13 on 2022-07-06 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bclabels', '0045_auto_20220512_2023'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bclabel',
            old_name='default_text',
            new_name='label_text',
        ),
    ]
