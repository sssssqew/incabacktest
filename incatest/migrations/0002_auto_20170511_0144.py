# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-11 01:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incatest', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wdate', models.DateField(blank=True, null=True)),
                ('interest', models.DecimalField(blank=True, decimal_places=17, max_digits=30, null=True)),
                ('interest_sum', models.DecimalField(blank=True, decimal_places=17, max_digits=30, null=True)),
                ('interest_index', models.DecimalField(blank=True, decimal_places=17, max_digits=30, null=True)),
                ('interest_index_sum', models.DecimalField(blank=True, decimal_places=17, max_digits=30, null=True)),
                ('interest_score', models.DecimalField(blank=True, decimal_places=17, max_digits=30, null=True)),
                ('interest_score_sum', models.DecimalField(blank=True, decimal_places=17, max_digits=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemcode', models.CharField(blank=True, max_length=20, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='log',
            name='result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='incatest.Result'),
        ),
    ]