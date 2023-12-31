# Generated by Django 3.1.13 on 2021-12-02 22:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0025_institution_created'),
        ('projects', '0085_auto_20211202_2228'),
        ('helpers', '0015_connections'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstitutionNotice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notice_type', models.CharField(choices=[('open_to_collaboration', 'open_to_collaboration'), ('attribution_incomplete', 'attribution_incomplete'), ('open_to_collaboration_and_attribution_incomplete', 'open_to_collaboration_and_attribution_incomplete')], max_length=50, null=True)),
                ('open_to_collaboration_img_url', models.URLField(blank=True, null=True)),
                ('open_to_collaboration_default_text', models.TextField(blank=True, null=True)),
                ('attribution_incomplete_img_url', models.URLField(blank=True, null=True)),
                ('attribution_incomplete_default_text', models.TextField(blank=True, null=True)),
                ('archived', models.BooleanField(blank=True, default=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='institutions.institution')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_institutional_notice', to='projects.project')),
            ],
            options={
                'verbose_name': 'Institution Notice',
                'verbose_name_plural': 'Institution Notices',
                'ordering': ('-created',),
            },
        ),
    ]
