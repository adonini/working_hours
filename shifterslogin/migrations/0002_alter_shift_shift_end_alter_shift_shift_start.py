# Generated by Django 5.0.6 on 2024-08-02 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shifterslogin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='shift_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shift',
            name='shift_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]