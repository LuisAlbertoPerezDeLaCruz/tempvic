# Generated by Django 2.1.7 on 2019-03-28 05:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20190326_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actividad',
            name='ac_fdesp',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 3, 28, 5, 54, 52, 693468), null=True),
        ),
        migrations.AlterField(
            model_name='serie',
            name='s_empieza',
            field=models.DateField(default=datetime.datetime(2019, 3, 28, 5, 54, 52, 695272)),
        ),
        migrations.AlterField(
            model_name='serie',
            name='s_termina_date',
            field=models.DateField(default=datetime.datetime(2019, 3, 28, 5, 54, 52, 695329)),
        ),
    ]