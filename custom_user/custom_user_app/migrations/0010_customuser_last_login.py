# Generated by Django 4.0.6 on 2022-10-28 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user_app', '0009_remove_customuser_last_login'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]