# Generated by Django 3.0.7 on 2021-07-27 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0029_auto_20210727_0933'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='project_date_ongoing',
            new_name='publication_date_ongoing',
        ),
    ]
