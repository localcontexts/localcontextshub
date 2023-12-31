# Generated by Django 3.1.13 on 2022-06-14 12:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0032_remove_researcher_projects'),
        ('institutions', '0026_remove_institution_projects'),
        ('helpers', '0020_auto_20220504_2258'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenToCollaborateNoticeURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='institutions.institution')),
                ('researcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='researchers.researcher')),
            ],
            options={
                'verbose_name': 'Open To Collaborate Notice URL',
                'verbose_name_plural': 'Open To Collaborate Notice URLs',
            },
        ),
    ]
