# Generated by Django 3.1.13 on 2021-11-17 21:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0040_community_created'),
        ('researchers', '0029_auto_20211001_1916'),
        ('institutions', '0025_institution_created'),
        ('helpers', '0014_labelnote'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connections',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('communities', models.ManyToManyField(blank=True, db_index=True, related_name='communities_connected', to='communities.Community')),
                ('community', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='community_connections', to='communities.community')),
                ('institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='institution_connections', to='institutions.institution')),
                ('institutions', models.ManyToManyField(blank=True, db_index=True, related_name='institutions_connected', to='institutions.Institution')),
                ('researcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='researcher_connections', to='researchers.researcher')),
                ('researchers', models.ManyToManyField(blank=True, db_index=True, related_name='researchers_connected', to='researchers.Researcher')),
            ],
            options={
                'verbose_name': 'Connections',
                'verbose_name_plural': 'Connections',
            },
        ),
    ]
