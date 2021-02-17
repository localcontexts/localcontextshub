# Generated by Django 3.0.7 on 2021-01-21 23:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0013_auto_20210120_2254'),
        ('notifications', '0008_auto_20210121_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitynotification',
            name='community',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='communities.Community'),
        ),
        migrations.AlterField(
            model_name='communitynotification',
            name='notification_type',
            field=models.CharField(choices=[('requests', 'Requests'), ('labels', 'Labels'), ('relationships', 'Relationships')], max_length=20, null=True),
        ),
    ]
