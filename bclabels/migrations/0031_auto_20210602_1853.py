# Generated by Django 3.0.7 on 2021-06-02 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tklabels', '0012_remove_tknotice_statuses'),
        ('bclabels', '0030_remove_bcnotice_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bcnotice',
            name='statuses',
        ),
        migrations.DeleteModel(
            name='NoticeStatus',
        ),
    ]
