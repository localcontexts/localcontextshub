# Generated by Django 3.1.13 on 2022-09-09 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0037_auto_20220909_2306'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='notice',
            name='helpers_not_project_844147_idx',
        ),
        migrations.RemoveIndex(
            model_name='projectcomment',
            name='helpers_pro_project_4a7394_idx',
        ),
        migrations.RemoveIndex(
            model_name='projectstatus',
            name='helpers_pro_project_9d2572_idx',
        ),
        migrations.AddIndex(
            model_name='labelnote',
            index=models.Index(fields=['bclabel', 'tklabel'], name='helpers_lab_bclabel_226891_idx'),
        ),
        migrations.AddIndex(
            model_name='labeltranslation',
            index=models.Index(fields=['bclabel', 'tklabel'], name='helpers_lab_bclabel_fc30f1_idx'),
        ),
        migrations.AddIndex(
            model_name='notice',
            index=models.Index(fields=['project', 'researcher', 'institution'], name='helpers_not_project_6ea156_idx'),
        ),
        migrations.AddIndex(
            model_name='opentocollaboratenoticeurl',
            index=models.Index(fields=['institution', 'researcher'], name='helpers_ope_institu_f0c7a8_idx'),
        ),
        migrations.AddIndex(
            model_name='projectcomment',
            index=models.Index(fields=['project', 'community', 'sender'], name='helpers_pro_project_3d97d1_idx'),
        ),
        migrations.AddIndex(
            model_name='projectstatus',
            index=models.Index(fields=['project', 'community'], name='helpers_pro_project_b7bfbd_idx'),
        ),
    ]
