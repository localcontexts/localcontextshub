# Generated by Django 3.0.7 on 2021-07-27 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0028_auto_20210614_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_date_ongoing',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='project_image2',
            field=models.ImageField(blank=True, null=True, upload_to='users/project-images'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_image3',
            field=models.ImageField(blank=True, null=True, upload_to='users/project-images'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_image4',
            field=models.ImageField(blank=True, null=True, upload_to='users/project-images'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_image5',
            field=models.ImageField(blank=True, null=True, upload_to='users/project-images'),
        ),
    ]
