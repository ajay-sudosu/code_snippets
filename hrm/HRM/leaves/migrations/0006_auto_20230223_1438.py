# Generated by Django 3.2.17 on 2023-02-23 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaves', '0005_auto_20230223_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavesdetails',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='leavesdetails',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]