# Generated by Django 3.0.7 on 2021-05-20 18:30

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0021_auto_20210520_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='unique_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True, unique=True),
        ),
    ]
