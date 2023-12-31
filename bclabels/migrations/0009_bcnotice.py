# Generated by Django 3.0.7 on 2021-01-18 20:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0012_delete_usercommunity'),
        ('researchers', '0003_auto_20210114_2032'),
        ('bclabels', '0008_auto_20201228_2358'),
    ]

    operations = [
        migrations.CreateModel(
            name='BCNotice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('communities', models.ManyToManyField(blank=True, related_name='bcnotice_communities', to='communities.Community')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='researchers.Project')),
            ],
            options={
                'verbose_name': 'BC Notice',
                'verbose_name_plural': 'BC Notices',
            },
        ),
    ]
