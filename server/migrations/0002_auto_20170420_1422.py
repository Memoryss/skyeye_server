# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-20 06:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='editor',
            name='stop_time',
            field=models.IntegerField(default=0),
        ),
    ]
