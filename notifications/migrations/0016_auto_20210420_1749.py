# Generated by Django 3.0.7 on 2021-04-20 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0015_noticecomment_noticestatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticestatus',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', 'pending'), ('not_pending', 'not_pending')], max_length=20, null=True),
        ),
        migrations.DeleteModel(
            name='NoticeComment',
        ),
    ]
