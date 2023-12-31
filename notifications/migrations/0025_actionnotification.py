# Generated by Django 3.0.7 on 2021-05-11 19:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0017_researcher_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('institutions', '0011_auto_20210510_2022'),
        ('communities', '0021_auto_20210511_1704'),
        ('notifications', '0024_noticecomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('notification_type', models.CharField(choices=[('Labels', 'labels'), ('Connections', 'connections'), ('Activity', 'activity'), ('Projects', 'projects')], max_length=20, null=True)),
                ('reference_id', models.CharField(blank=True, max_length=50, null=True)),
                ('viewed', models.BooleanField(default=False)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('community', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='communities.Community')),
                ('institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='institutions.Institution')),
                ('researcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='researchers.Researcher')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Action Notification',
                'verbose_name_plural': 'Action Notifications',
                'ordering': ('-created',),
            },
        ),
    ]
