# Generated by Django 3.1.13 on 2022-09-28 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0039_auto_20220920_1831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectstatus',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', 'pending'), ('not_pending', 'not_pending'), ('labels_applied', 'labels_applied')], max_length=20, null=True),
        ),
    ]
