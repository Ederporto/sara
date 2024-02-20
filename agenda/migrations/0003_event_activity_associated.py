# Generated by Django 4.1.7 on 2024-02-19 03:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0013_activity_is_main_activity'),
        ('agenda', '0002_event_metric_associated'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='activity_associated',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='event_activity', to='metrics.activity'),
        ),
    ]
