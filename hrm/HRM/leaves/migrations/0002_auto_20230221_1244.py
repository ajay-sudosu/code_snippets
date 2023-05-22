# Generated by Django 3.2.17 on 2023-02-21 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaves', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaves',
            name='attachments',
            field=models.FileField(blank=True, null=True, upload_to='attachments/'),
        ),
        migrations.AlterField(
            model_name='leaves',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Pending', 'Pending'), ('Cancelled', 'Cancelled'), ('Partialaccepted', 'Partialaccepted')], default='Pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='leavesdetails',
            name='leave_type',
            field=models.CharField(choices=[('Fullday', 'Fullday'), ('Halfday', 'Halfday'), ('Shortleave', 'Shortleave')], default='Fullday', max_length=10),
        ),
        migrations.AlterField(
            model_name='leavesdetails',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Pending', 'Pending'), ('Cancelled', 'Cancelled')], default='PENDING', max_length=12),
        ),
    ]