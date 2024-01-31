# Generated by Django 4.1.7 on 2024-01-20 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0029_report_number_of_people_reached_through_social_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='number_of_community_communications',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='report',
            name='number_of_events',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='report',
            name='number_of_mentions',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='report',
            name='number_of_new_followers',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
