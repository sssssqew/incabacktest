# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-08 07:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incatest', '0011_fund'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='fund',
            table='stock_itemcode',
        ),
    ]