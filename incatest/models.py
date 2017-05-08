# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


# Create your models here.
class incaResults(models.Model):
	wdate = models.CharField(max_length=10,  blank=True, null=True)
	itemcode = models.CharField(max_length=20,  blank=True, null=True)
	itemname = models.CharField(max_length=100,  blank=True, null=True)
	DNA_score = models.DecimalField(max_digits=22, decimal_places=12, blank=True, null=True)
	DNA_index = models.DecimalField(max_digits=22, decimal_places=12, blank=True, null=True)
	probability = models.DecimalField(max_digits=22, decimal_places=12, blank=True, null=True)
	MAX_rate = models.IntegerField(default=0)
	MIN_rate = models.IntegerField(default=0)

	class Meta:
		db_table = 'time_series_1Y_inverse'

	def publish(self):
		self.created_date = timezone.now()
		
	def change(self):
		self.updated_date = timezone.now()

	def __str__(self):
		return self.itemname.encode('utf-8')



