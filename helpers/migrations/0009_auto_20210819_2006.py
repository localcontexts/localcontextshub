# Generated by Django 3.0.7 on 2021-08-19 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0008_auto_20210819_1647'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='noticecomment',
            options={'ordering': ('created',), 'verbose_name': 'Notice Comment', 'verbose_name_plural': 'Notice Comments'},
        ),
        migrations.RemoveField(
            model_name='noticecomment',
            name='bcnotice',
        ),
        migrations.RemoveField(
            model_name='noticecomment',
            name='tknotice',
        ),
        migrations.RemoveField(
            model_name='noticestatus',
            name='bcnotice',
        ),
        migrations.RemoveField(
            model_name='noticestatus',
            name='tknotice',
        ),
    ]
