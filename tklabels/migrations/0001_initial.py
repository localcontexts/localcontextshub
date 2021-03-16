# Generated by Django 3.0.7 on 2021-03-16 18:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('institutions', '0006_auto_20210127_2132'),
        ('communities', '0015_auto_20210201_2119'),
        ('researchers', '0016_auto_20210224_0052'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0005_auto_20210312_2027'),
    ]

    operations = [
        migrations.CreateModel(
            name='TKNotice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, max_length=1500, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('communities', models.ManyToManyField(blank=True, related_name='tknotice_communities', to='communities.Community')),
                ('placed_by_institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='institutions.Institution')),
                ('placed_by_researcher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='researchers.Researcher')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.Project')),
            ],
            options={
                'verbose_name': 'TK Notice',
                'verbose_name_plural': 'TK Notices',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='TKLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label_type', models.CharField(choices=[('attribution', 'attribution'), ('clan', 'clan'), ('family', 'family'), ('outreach', 'outreach'), ('tk_multiple_community', 'tk_multiple_community'), ('outreach', 'outreach'), ('non_verified', 'non_verified'), ('verified', 'verified'), ('non_commercial', 'non_commercial'), ('commercial', 'commercial'), ('culturally_sensitive', 'culturally_sensitive'), ('community_voice', 'community_voice'), ('community_use_only', 'community_use_only'), ('seasonal', 'seasonal'), ('women_general', 'women_general'), ('men_general', 'men_general'), ('men_restricted', 'men_restricted'), ('women_restricted', 'women_restricted'), ('secret_sacred', 'secret_sacred')], max_length=50, null=True)),
                ('name', models.CharField(max_length=90, null=True, verbose_name='label name')),
                ('default_text', models.TextField(blank=True, null=True)),
                ('modified_text', models.TextField(blank=True, null=True)),
                ('is_approved', models.BooleanField(default=False, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('community', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='communities.Community')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('tk_notice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='tklabels.TKNotice')),
            ],
            options={
                'verbose_name': 'TK Label',
                'verbose_name_plural': 'TK Labels',
                'ordering': ('-created',),
            },
        ),
    ]
