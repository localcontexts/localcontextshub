# Generated by Django 4.2.11 on 2024-05-28 14:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("institutions", "0034_remove_institution_approved_by_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="institution",
            name="is_submitted",
        ),
    ]