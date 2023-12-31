# Generated by Django 3.0.7 on 2021-08-12 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bclabels', '0035_bcnotice_default_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bclabel',
            name='label_type',
            field=models.CharField(choices=[('provenance', 'provenance'), ('commercialization', 'commercialization'), ('non_commercial', 'non_commercial'), ('collaboration', 'collaboration'), ('consent_verified', 'consent_verified'), ('consent_non_verified', 'consent_non_verified'), ('multiple_community', 'multiple_community'), ('research', 'research'), ('clan', 'clan'), ('outreach', 'outreach')], max_length=20, null=True),
        ),
    ]
