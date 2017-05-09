# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from background_task import background
from .models import Outcome, Price, Fund, File

import csv
import json
import os
from os.path import join

from datetime import datetime
from datetime import timedelta

# Create your views here.
def index(request):
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

	# prices = Price.objects.filter(itemcode='KLVL01V2101', wdate__range=['2015-04-20', '2015-05-10'])
	# for price in prices:
	# 	print " -------------------------- "
	# 	print price.itemcode
	# 	print price.wdate
	# 	# print price.open
	# 	# print price.high
	# 	# print price.low
	# 	print price.close
	# 	print price.trading_volume
	# 	print price.trading_value
	# 	print " ---------------------------- "
	# 	cnt = cnt + 1
	# print type('2014-04-13')

	files = []
	for file in os.listdir(settings.MEDIA_ROOT):
		files.append(os.path.splitext(file)[0])
		print os.path.splitext(file)[0]
	context = {'files':files}
	return render(request, "incatest/index.html", context)
	# return HttpResponse(cnt)

def show(request, fname):
	rows = []
	filename = fname + '.csv'
	filepath = join(settings.MEDIA_ROOT, filename)
	with open(filepath, 'r') as f:
		reader = csv.reader(f, delimiter=str(',')) 
		for row in reader: 
			rows.append(row)
			# print row

	context = {'rows':rows}
	return render(request, 'incatest/show.html', context)


def create(request):
	funds = Fund.objects.all()
	context = {'funds':funds}

	return render(request, "incatest/create.html", context)

@background(queue='my-queue')
def writetocsv(filepath, prices_ids):
	prices = Price.objects.filter(id__in=prices_ids)
	with open(filepath, 'w') as f:
		writer = csv.writer(f, csv.excel)
		for price in prices:
			writer.writerow([price.itemcode.encode('euc-kr'), price.wdate, price.close])

def store(request):
	today = datetime.now().strftime("%Y%m%d")
	selected_code = request.POST.get('code-list')
	# print selected_code
	s_date = request.POST.get("s_date")
	e_date = request.POST.get("e_date")
	# print s_date
	prices = Price.objects.filter(itemcode=selected_code, wdate__range=[s_date, e_date])

	# Create path of file
	filename = "insu_" + s_date + "_to_" + e_date + ".csv"
	filepath = join(settings.MEDIA_ROOT, filename)
	print filepath

	# for idx in prices.values_list('id', flat=True):
	# 	print Price.objects.get(pk=idx).itemcode
	prices_ids = tuple(prices.values_list('id', flat=True))
	writetocsv(filepath, prices_ids)
	
	# return HttpResponse("store")
	return HttpResponseRedirect(reverse('insu_index'))