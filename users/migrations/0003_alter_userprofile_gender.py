# Generated by Django 4.1.7 on 2023-04-21 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_userprofile_wiki_handle_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('1', 'Male'), ('2', 'Female'), ('3', 'Non Binary'), ('4', 'Other')], default='4', max_length=2, null=True),
        ),
    ]
