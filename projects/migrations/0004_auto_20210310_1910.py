# Generated by Django 3.0.7 on 2021-03-10 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20210309_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_contact',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_contact_email',
            field=models.EmailField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='publication_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
