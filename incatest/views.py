# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import Outcome, Price, Fund

import csv
import json

from datetime import datetime
from datetime import timedelta

# Create your views here.
def index(requesst):
	cnt = 0
	# outcomes = Outcome.objects.all()
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

	prices = Price.objects.filter(itemcode='KLVL01V2101', wdate__range=['2015-04-20', '2015-05-10'])
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


def create(request):
	funds = Fund.objects.all()
	context = {'funds':funds}
	
	return render(request, "incatest/create.html", context)


def store(request):
	return HttpResponse("store")