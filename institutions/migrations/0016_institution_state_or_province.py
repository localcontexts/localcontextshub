# Generated by Django 3.0.7 on 2021-06-15 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0015_auto_20210615_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='state_or_province',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='state or province'),
        ),
    ]
