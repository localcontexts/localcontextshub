# Generated by Django 3.1 on 2020-09-07 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0004_usercommunity_userinstitution_users'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Community',
        ),
        migrations.DeleteModel(
            name='Institutions',
        ),
        migrations.DeleteModel(
            name='UserCommunity',
        ),
        migrations.DeleteModel(
            name='UserInstitution',
        ),
        migrations.DeleteModel(
            name='Users',
        ),
    ]
