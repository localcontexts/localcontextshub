# Generated by Django 3.1.13 on 2023-07-27 21:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0030_auto_20230607_2059'),
        ('researchers', '0035_auto_20221021_2043'),
        ('helpers', '0053_auto_20230629_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opentocollaboratenoticeurl',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='otc_institution_url', to='institutions.institution'),
        ),
        migrations.AlterField(
            model_name='opentocollaboratenoticeurl',
            name='researcher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='otc_researcher_url', to='researchers.researcher'),
        ),
        migrations.CreateModel(
            name='NoticeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notice_type', models.CharField(choices=[('biocultural', 'biocultural'), ('traditional_knowledge', 'traditional_knowledge'), ('attribution_incomplete', 'attribution_incomplete')], max_length=50, null=True)),
                ('language_tag', models.CharField(blank=True, max_length=5)),
                ('language', models.CharField(blank=True, max_length=150)),
                ('translated_name', models.CharField(blank=True, max_length=150)),
                ('translated_text', models.TextField(blank=True)),
                ('notice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notice_translations', to='helpers.notice')),
            ],
        ),
    ]
