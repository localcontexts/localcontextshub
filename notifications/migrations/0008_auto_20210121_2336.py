# Generated by Django 3.0.7 on 2021-01-21 23:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0013_auto_20210120_2254'),
        ('notifications', '0007_usernotification_role'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usernotification',
            options={'verbose_name': 'User Notification', 'verbose_name_plural': 'User Notifications'},
        ),
        migrations.CreateModel(
            name='CommunityNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('notification_type', models.CharField(choices=[('requests', 'Requests'), ('labels', 'Labels'), ('relationships', 'relationships')], max_length=20, null=True)),
                ('reference_id', models.CharField(blank=True, max_length=10, null=True)),
                ('viewed', models.BooleanField(default=False)),
                ('community', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='communities.Community')),
            ],
            options={
                'verbose_name': 'Community Notification',
                'verbose_name_plural': 'Community Notifications',
            },
        ),
    ]
