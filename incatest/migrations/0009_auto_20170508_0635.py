# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-08 06:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incatest', '0008_auto_20170508_0631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incaoutcomes',
            name='wdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='incaprices',
            name='wdate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
