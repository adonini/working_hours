# Generated by Django 5.0.6 on 2024-08-06 07:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shifterslogin', '0003_shift_shift_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Break',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('break_start', models.DateTimeField()),
                ('break_end', models.DateTimeField(blank=True, null=True)),
                ('break_active', models.BooleanField(default=True)),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='breaks', to='shifterslogin.shift')),
            ],
            options={
                'db_table': 'breaks',
            },
        ),
    ]
