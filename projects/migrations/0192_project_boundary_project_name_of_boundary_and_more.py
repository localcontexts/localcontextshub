# Generated by Django 4.2.11 on 2024-07-12 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0051_community_share_boundary_publicly'),
        ('projects', '0191_alter_project_project_privacy_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='boundary',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='communities.boundary'),
        ),
        migrations.AddField(
            model_name='project',
            name='name_of_boundary',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='source_of_boundary',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]
