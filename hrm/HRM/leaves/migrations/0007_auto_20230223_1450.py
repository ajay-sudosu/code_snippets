# Generated by Django 3.2.17 on 2023-02-23 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaves', '0006_auto_20230223_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavesdetails',
            name='end_time',
            field=models.TimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='leavesdetails',
            name='start_time',
            field=models.TimeField(blank=True, default=None, null=True),
        ),
    ]
