# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


# Create your models here.
class Outcome(models.Model):
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

	def adjustScore(self):
		adj_score = self.DNA_score
		
		if self.DNA_score > 10:
			adj_score = 10

		# print self.DNA_score
		# print adj_score

		return adj_score

	def adjustIndex(self):
		adj_index = self.DNA_index

		if self.DNA_index > 10:
			adj_index = 10

		# print self.DNA_index
		# print adj_index

		return adj_index

class Price(models.Model):
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

	def getInterest(self):
		next_item =  Price.objects.filter(wdate__gt=self.wdate).order_by('wdate').first()
		interest = (next_item.close-self.close)/self.close
		# print next_item.wdate
		# print self.wdate
		return interest



class Fund(models.Model):
	itemcode = models.CharField(max_length=20,  blank=True, null=True)
	itemname = models.CharField(max_length=100,  blank=True, null=True)
	countryCode = models.CharField(max_length=3,  blank=True, null=True)

	class Meta:
		db_table = 'stock_itemcode'


class File(models.Model):
	filename = models.FileField(upload_to='%Y%m%d', blank=True, null=True)








