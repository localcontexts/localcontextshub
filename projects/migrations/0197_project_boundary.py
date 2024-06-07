# Generated by Django 4.2.11 on 2024-06-07 22:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0051_alter_invitemember_role'),
        ('projects', '0196_alter_project_related_projects'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='boundary',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='communities.boundary'),
        ),
    ]
