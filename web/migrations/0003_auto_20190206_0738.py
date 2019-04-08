# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-02-06 07:38
from __future__ import unicode_literals

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20181211_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='actividad',
            name='ac_imagenes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='actividad',
            name='ac_serieId_originaria',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='ac_fdesp',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 2, 6, 7, 38, 30, 289510), null=True),
        ),
        migrations.AlterField(
            model_name='serie',
            name='s_empieza',
            field=models.DateField(default=datetime.datetime(2019, 2, 6, 7, 38, 30, 291098)),
        ),
        migrations.AlterField(
            model_name='serie',
            name='s_termina_date',
            field=models.DateField(default=datetime.datetime(2019, 2, 6, 7, 38, 30, 291171)),
        ),
    ]
