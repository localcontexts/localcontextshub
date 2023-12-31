# Generated by Django 3.0.7 on 2021-05-05 23:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0010_auto_20210505_1733'),
        ('researchers', '0017_researcher_image'),
        ('communities', '0019_auto_20210505_1733'),
        ('projects', '0013_project_project_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectcontributors',
            name='community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='communities.Community'),
        ),
        migrations.AlterField(
            model_name='projectcontributors',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='institutions.Institution'),
        ),
        migrations.AlterField(
            model_name='projectcontributors',
            name='researcher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='researchers.Researcher'),
        ),
    ]
