# Generated by Django 3.0.7 on 2021-05-05 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0020_auto_20210504_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institutionnotification',
            name='notification_type',
            field=models.CharField(choices=[('Activity', 'activity'), ('Labels', 'labels'), ('Connections', 'connections'), ('Projects', 'projects')], max_length=20, null=True),
        ),
    ]
