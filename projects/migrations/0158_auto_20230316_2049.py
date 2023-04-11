# Generated by Django 3.1.13 on 2023-03-16 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0157_auto_20230302_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='related_projects',
            field=models.ManyToManyField(blank=True, related_name='_project_related_projects_+', to='projects.Project'),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('Contributor', 'Contributor'), ('Private', 'Private')], max_length=20, null=True),
        ),
    ]