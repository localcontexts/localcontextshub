# Generated by Django 3.1.13 on 2023-01-19 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0153_auto_20230105_2230'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectArchived',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_uuid', models.UUIDField(blank=True, db_index=True, null=True)),
                ('community_id', models.IntegerField(blank=True, null=True)),
                ('institution_id', models.IntegerField(blank=True, null=True)),
                ('researcher_id', models.IntegerField(blank=True, null=True)),
                ('archived', models.BooleanField()),
            ],
            options={
                'verbose_name_plural': 'Project Archived',
            },
        ),
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Discoverable', 'Discoverable'), ('Private', 'Private'), ('Public', 'Public')], max_length=20, null=True),
        ),
    ]
