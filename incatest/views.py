# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from background_task import background
from .models import Outcome, Price, Fund, Result, Log

import csv
import json
import re
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

	fnames = fname.split('_')
	# print fnames
	code = fnames[1]
	s_date = fnames[2]
	e_date = fnames[4]

	result = Result.objects.get(itemcode=code, start_date=s_date, end_date=e_date)

	with open(filepath, 'r') as f:
		reader = list(csv.reader(f, delimiter=str(',')))
		for row in reader: 
			if row != reader[-1]:
				date.append(row[1])
				# interest.append(row[3])
				# interest_index.append(row[5])
				# interest_score.append(row[7])
				log = Log.objects.get(result_id=result.id, wdate=row[1])
				print log.wdate
				print log.interest_sum
				interest.append(str(log.interest_sum))
				interest_index.append(str(log.interest_index_sum))
				interest_score.append(str(log.interest_score_sum))

				#누적수익률 추가 
				row.append(str(log.interest_sum))
				row.append(str(log.interest_index_sum))
				row.append(str(log.interest_score_sum))

			rows.append(row)

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

@background(queue='write-to-csv-3')
def writetocsv(filepath, prices_ids, result_id):
	# outcomes = Price.objects.filter(id__in=outcomes_ids)
	prices = Price.objects.filter(id__in=prices_ids)
	# result = Result.objects.get(id=result_id)

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
			interest = 0
			interest = price.getInterest()
			# print interest
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
			
			# save backtest result in db
			try:
				log = Log.objects.get(result_id=result_id, wdate=price.wdate)
				print "log already exists in db"
			except:
				log = Log(
					result_id = result_id, 
					wdate = price.wdate, 
					interest = interest,
					interest_sum = total_interest,
					interest_index = interest_index,
					interest_index_sum = total_interest_index,
					interest_score = interest_score,
					interest_score_sum = total_interest_score
				)
				log.save() 

			# save in file 
			writer.writerow([price.itemcode.encode('euc-kr'), price.wdate, 10, interest, adj_index, interest_index, adj_score, interest_score])
		writer.writerow([price.itemcode.encode('euc-kr'), "Total", total_weight, total_interest, total_index, total_interest_index, total_score, total_interest_score])
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
	filename = "insu_" + selected_code + '_' + s_date + "_to_" + e_date + ".csv"
	filepath = join(settings.MEDIA_ROOT, filename)
	print filepath

	# for idx in prices.values_list('id', flat=True):
	# 	print Price.objects.get(pk=idx).itemcode

	# print outcomes
	# cnt = 0
	# for outcome in outcomes:
	# 	cnt = cnt + 1
	# 	print outcome.wdate

	try:
		result = Result.objects.get(itemcode=selected_code, start_date=s_date, end_date=e_date)
	except:
		result = Result(
			itemcode = selected_code, 
			start_date = s_date, 
			end_date = e_date
		)
		result.save() 

	# outcomes_ids = tuple(outcomes.values_list('id', flat=True))
	prices_ids = tuple(prices.values_list('id', flat=True))
	writetocsv(filepath, prices_ids, result.id)
	# print cnt 
	
	# return HttpResponse("store")
	return HttpResponseRedirect(reverse('insu_index'))