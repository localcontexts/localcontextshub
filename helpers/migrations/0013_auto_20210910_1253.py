# Generated by Django 3.0.7 on 2021-09-10 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0012_notice_archived'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projectcomment',
            options={'ordering': ('created',), 'verbose_name': 'Project Comment', 'verbose_name_plural': 'Project Comments'},
        ),
        migrations.AlterModelOptions(
            name='projectstatus',
            options={'verbose_name': 'Project Status', 'verbose_name_plural': 'Project Statuses'},
        ),
    ]
