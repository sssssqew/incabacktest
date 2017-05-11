# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-11 01:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemcode', models.CharField(blank=True, max_length=20, null=True)),
                ('itemname', models.CharField(blank=True, max_length=100, null=True)),
                ('countryCode', models.CharField(blank=True, max_length=3, null=True)),
            ],
            options={
                'db_table': 'stock_itemcode',
            },
        ),
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wdate', models.CharField(blank=True, max_length=10, null=True)),
                ('itemcode', models.CharField(blank=True, max_length=20, null=True)),
                ('itemname', models.CharField(blank=True, max_length=100, null=True)),
                ('DNA_score', models.DecimalField(blank=True, decimal_places=17, max_digits=30, null=True)),
                ('DNA_index', models.DecimalField(blank=True, decimal_places=17, max_digits=30, null=True)),
                ('probability', models.DecimalField(blank=True, decimal_places=17, max_digits=30, null=True)),
                ('MAX_rate', models.IntegerField()),
                ('MIN_rate', models.IntegerField()),
            ],
            options={
                'db_table': 'time_series_1Y_inverse',
            },
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemcode', models.CharField(blank=True, max_length=20, null=True)),
                ('wdate', models.CharField(blank=True, max_length=10, null=True)),
                ('open', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('high', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('low', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('close', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('trading_volume', models.IntegerField()),
                ('trading_value', models.IntegerField()),
            ],
            options={
                'db_table': 'stock_data',
            },
        ),
    ]
