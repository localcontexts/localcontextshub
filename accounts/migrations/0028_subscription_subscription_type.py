# Generated by Django 5.0.6 on 2024-08-23 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_serviceproviderconnections'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='subscription_type',
            field=models.CharField(choices=[('individual', 'Individual'), ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('cc_notice_only', 'CC Notice Only'), ('cc_notices', 'CC Notices')], default='Not-Set', max_length=20),
            preserve_default=False,
        ),
    ]