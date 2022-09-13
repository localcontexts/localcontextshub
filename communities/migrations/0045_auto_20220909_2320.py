# Generated by Django 3.1.13 on 2022-09-09 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0044_auto_20220909_2318'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='community',
            name='communities_communi_4fae5c_idx',
        ),
        migrations.AddIndex(
            model_name='community',
            index=models.Index(fields=['id', 'community_creator', 'image'], name='communities_id_6c41e3_idx'),
        ),
    ]
