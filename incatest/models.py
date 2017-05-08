# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


# Create your models here.
class incaoutcomes(models.Model):
	wdate = models.DateField(blank=True, null=True)
	itemcode = models.CharField(max_length=20,  blank=True, null=True)
	itemname = models.CharField(max_length=100,  blank=True, null=True)
	DNA_score = models.DecimalField(max_digits=30, decimal_places=17, blank=True, null=True)
	DNA_index = models.DecimalField(max_digits=30, decimal_places=17, blank=True, null=True)
	probability = models.DecimalField(max_digits=30, decimal_places=17, blank=True, null=True)
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


class incaprices(models.Model):
	itemcode = models.CharField(max_length=20,  blank=True, null=True)
	wdate = models.DateField(blank=True, null=True)
	open = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
	high = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
	low = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
	close = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
	trading_volume = models.IntegerField(default=0)
	trading_value = models.IntegerField(default=0)

	class Meta:
		db_table = 'stock_data'

	def publish(self):
		self.created_date = timezone.now()
		
	def change(self):
		self.updated_date = timezone.now()

	def __str__(self):
		return self.itemcode.encode('utf-8')




