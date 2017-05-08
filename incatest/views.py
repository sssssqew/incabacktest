# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import incaoutcomes, incaprices

import csv
import json

from datetime import datetime
from datetime import timedelta

# Create your views here.
def index(requesst):
	cnt = 0
	# outcomes = incaoutcomes.objects.all()
	# for outcome in outcomes:
	# 	if cnt < 10:
	# 		print " -------------------------- "
	# 		print outcome.wdate
	# 		print outcome.itemcode
	# 		print outcome.DNA_score
	# 		print outcome.DNA_index
	# 		print outcome.probability
	# 		print outcome.MAX_rate
	# 		print outcome.MIN_rate
	# 		print " ---------------------------- "

	prices = incaprices.objects.filter(itemcode='KLVL01V2101', wdate__gte='2015-04-20', wdate__lte='2015-04-30')
	for price in prices:
		print " -------------------------- "
		print price.itemcode
		print price.wdate
		# print price.open
		# print price.high
		# print price.low
		print price.close
		print price.trading_volume
		print price.trading_value
		print " ---------------------------- "
		cnt = cnt + 1
	return HttpResponse(cnt)
