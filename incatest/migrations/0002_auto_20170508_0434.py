# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-08 04:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incatest', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='incaResults',
            new_name='incaoutcomes',
        ),
    ]
