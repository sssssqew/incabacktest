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

	date = []
	interest = []
	interest_index = []
	interest_score = []

	filename = fname + '.csv'
	filepath = join(settings.MEDIA_ROOT, filename)
	with open(filepath, 'r') as f:
		reader = list(csv.reader(f, delimiter=str(',')))
		for row in reader: 
			rows.append(row)
			if row != reader[-1]:
				date.append(row[1])
				interest.append(row[2])
				interest_index.append(row[5])
				interest_score.append(row[7])

	date.insert(0, 'x')
	interest.insert(0, '일간수익률')
	interest_index.insert(0, '일간수익률(Index)')
	interest_score.insert(0, '일간수익률(Score)')

	columns = [date, interest, interest_index, interest_score]
	context = {'columns': json.dumps(columns), 'rows':rows}
	return render(request, 'incatest/show.html', context)


def create(request):
	funds = Fund.objects.all()
	context = {'funds':funds}

	return render(request, "incatest/create.html", context)

@background(queue='my-queue')
def writetocsv(filepath, prices_ids):
	# outcomes = Price.objects.filter(id__in=outcomes_ids)
	prices = Price.objects.filter(id__in=prices_ids)

	total_interest = 0
	total_weight = 0
	total_index = 0
	total_interest_index = 0
	total_score = 0
	total_interest_score = 0

	cnt = 0
	with open(filepath, 'w') as f:
		writer = csv.writer(f, csv.excel)
		for price in prices:
			
			interest = price.getInterest()
			total_interest += interest
			total_weight += 10

			adj_score = 0
			adj_index = 0
			interest_score = 0
			interest_index = 0
		
			try:
				outcome = Outcome.objects.get(wdate=price.wdate, itemcode=price.itemcode)
				adj_score = outcome.adjustScore()
				adj_index = outcome.adjustIndex()

				interest_score = (interest * adj_score)/10
				interest_index = (interest * adj_index)/10

				total_score += adj_score
				total_index += adj_index

				total_interest_index += interest_index
				total_interest_score += interest_score

				# print "--------    score ----------"
				# print adj_score
				# print outcome.DNA_score
				# print "--------    index ----------"
				# print adj_index
				# print outcome.DNA_index

				# print "-----------------------------------------------"
				# print outcome.wdate
				cnt = cnt + 1
				# print "----------- interest_score --------------------------------"
				# print interest_score 
			except:
				print "outcome related to price doesn't exist"
			# print price.wdate 
			
			writer.writerow([price.itemcode.encode('euc-kr'), price.wdate, interest, 10, adj_index, interest_index, adj_score, interest_score])
		writer.writerow([price.itemcode.encode('euc-kr'), "Total", total_interest, total_weight, total_index, total_interest_index, total_score, total_interest_score])
	# print cnt

def store(request):
	today = datetime.now().strftime("%Y%m%d")
	selected_code = request.POST.get('code-list')
	print selected_code

	s_date = request.POST.get("s_date")
	e_date = request.POST.get("e_date")
	# print s_date
	# outcomes = Outcome.objects.filter(itemcode=selected_code, wdate__range=[s_date, e_date])
	prices = Price.objects.filter(itemcode=selected_code, wdate__range=[s_date, e_date])

	# Create path of file
	filename = "insu_" + s_date + "_to_" + e_date + ".csv"
	filepath = join(settings.MEDIA_ROOT, filename)
	print filepath

	# for idx in prices.values_list('id', flat=True):
	# 	print Price.objects.get(pk=idx).itemcode

	# print outcomes
	# cnt = 0
	# for outcome in outcomes:
	# 	cnt = cnt + 1
	# 	print outcome.wdate

	# outcomes_ids = tuple(outcomes.values_list('id', flat=True))
	prices_ids = tuple(prices.values_list('id', flat=True))
	writetocsv(filepath, prices_ids)
	# print cnt 
	
	# return HttpResponse("store")
	return HttpResponseRedirect(reverse('insu_index'))