# Generated by Django 3.1.13 on 2022-07-19 21:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0027_auto_20220719_1806'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notice',
            old_name='bc_default_text',
            new_name='default_text',
        ),
        migrations.RenameField(
            model_name='notice',
            old_name='bc_img_url',
            new_name='img_url',
        ),
        migrations.RenameField(
            model_name='notice',
            old_name='bc_svg_url',
            new_name='svg_url',
        ),
    ]
