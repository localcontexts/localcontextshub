# Generated by Django 3.0.7 on 2021-02-24 00:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('communities', '0015_auto_20210201_2119'),
        ('institutions', '0006_auto_20210127_2132'),
        ('researchers', '0015_project_project_type'),
        ('bclabels', '0018_auto_20210129_0210'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectContributors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('community', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='communities.Community')),
                ('institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='institutions.Institution')),
                ('researcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='researchers.Researcher')),
            ],
            options={
                'verbose_name': 'Project Contributors',
                'verbose_name_plural': 'Project Contributors',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_type', models.CharField(choices=[('Item', 'Item'), ('Collection', 'Collection'), ('Expedition', 'Expedition'), ('Publication', 'Publication')], max_length=20, null=True)),
                ('title', models.TextField(null=True)),
                ('description', models.TextField(null=True)),
                ('principal_investigator', models.CharField(blank=True, max_length=100, null=True)),
                ('principal_investigator_affiliation', models.CharField(blank=True, max_length=100, null=True)),
                ('project_contact', models.CharField(blank=True, max_length=100, null=True)),
                ('project_contact_email', models.EmailField(blank=True, max_length=100, null=True)),
                ('publication_doi', models.CharField(blank=True, max_length=200, null=True)),
                ('project_data_guid', models.CharField(blank=True, max_length=200, null=True)),
                ('recommended_citation', models.CharField(blank=True, max_length=200, null=True)),
                ('geome_project_id', models.IntegerField(blank=True, null=True)),
                ('source', models.TextField(blank=True, null=True)),
                ('url', models.TextField(blank=True, null=True)),
                ('publication_date', models.TextField(blank=True, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('is_public', models.BooleanField(default=True, null=True)),
                ('bclabels', models.ManyToManyField(blank=True, related_name='project_labels', to='bclabels.BCLabel', verbose_name='BC Labels')),
                ('contributors', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='projects.ProjectContributors')),
            ],
            options={
                'ordering': ('-date_added',),
            },
        ),
    ]
