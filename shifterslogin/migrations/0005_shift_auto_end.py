# Generated by Django 5.0.6 on 2024-08-07 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shifterslogin', '0004_break'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='auto_end',
            field=models.BooleanField(default=False),
        ),
    ]
