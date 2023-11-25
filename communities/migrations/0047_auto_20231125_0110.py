# Generated by Django 3.1.14 on 2023-11-25 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0046_auto_20231124_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coordinate',
            name='latitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name='coordinate',
            name='longitude',
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
    ]
