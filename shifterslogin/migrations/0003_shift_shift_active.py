# Generated by Django 5.0.6 on 2024-08-04 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shifterslogin', '0002_alter_shift_shift_end_alter_shift_shift_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='shift_active',
            field=models.BooleanField(default=True),
        ),
    ]
