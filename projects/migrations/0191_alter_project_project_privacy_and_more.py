# Generated by Django 4.2.11 on 2024-06-11 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0190_merge_20240126_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('Contributor', 'Contributor'), ('Private', 'Private')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='related_projects',
            field=models.ManyToManyField(blank=True, db_index=True, related_name='related_projects', to='projects.project', verbose_name='Related Projects'),
        ),
    ]