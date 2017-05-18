# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from background_task import background
from .models import Outcome, Price, Fund, Result, Log, InterVSInvest

import csv
import json
import re
import os
from os.path import join

from datetime import datetime
from datetime import timedelta
from decimal import *

# Create your views here.
def index(request):
	results = Result.objects.all()
	context = {"results":results}
	return render(request, "incatest/index.html", context)

def show(request, result):

	logs = Log.objects.filter(result=result)
	wdate = list(map(lambda x: str(x[0]), logs.values_list('wdate')))
	intervsinvest_sum = list(map(lambda x: str(x[0]), logs.values_list('intervsinvest_sum')))
	intervsinvest_index_sum = list(map(lambda x: str(x[0]), logs.values_list('intervsinvest_index_sum')))
	intervsinvest_score_sum = list(map(lambda x: str(x[0]), logs.values_list('intervsinvest_score_sum')))
	intervsinvest_index_score_sum = list(map(lambda x: str(x[0]), logs.values_list('intervsinvest_index_score_sum')))
	last_log = logs.last()

	wdate.insert(0, 'x')
	intervsinvest_sum.insert(0, '보유수익률')
	intervsinvest_index_sum.insert(0, 'DNA-리스크 based 수익률')
	intervsinvest_score_sum.insert(0, 'DNA-리턴 based 수익률')
	intervsinvest_index_score_sum.insert(0, 'DNA-리턴-리스크 based 수익률')

	columns_sum = [wdate, intervsinvest_sum, intervsinvest_index_sum, intervsinvest_score_sum, intervsinvest_index_score_sum]

	context = {"logs":logs, "last_log":last_log, 'columns_sum': json.dumps(columns_sum)}
	return render(request, 'incatest/show.html', context)

def create(request):
	funds = Fund.objects.all()
	context = {'funds':funds}

	return render(request, "incatest/create.html", context)

@background(queue='backtest')
def writetocsv(s_date, e_date, selected_code):
   # get prices
	try:
		prices = Price.objects.filter(itemcode=selected_code, wdate__range=[s_date, e_date])
		prices = prices.order_by('wdate')
	except:
		print "prices does not exist"

	# get outcomes
	try:
		outcomes = Outcome.objects.filter(itemcode=selected_code, wdate__range=[s_date, e_date])
		outcomes = outcomes.order_by('wdate')
	except:
		print "outcomes does not exist"

	# run test only if both prices and outcomes exist  
	if prices and outcomes:
		# create model to save backtest results
		try:
			result = Result.objects.get(itemcode=selected_code, start_date=s_date, end_date=e_date)
		except:
			result = Result(
				itemcode = selected_code, 
				start_date = s_date, 
				end_date = e_date
			)
			result.save()

		total_interest = 0
		total_weight = 0
		total_index = 0
		total_interest_index = 0
		total_score = 0
		total_interest_score = 0
		total_index_score = 0
		total_interest_index_score = 0

		# 투자대비 수익률 변수 
		intervsinvest = 0
		intervsinvest_index = 0
		intervsinvest_score = 0

		intervsinvest_sum = 0
		intervsinvest_index_sum = 0
		intervsinvest_score_sum = 0

		cnt = 0
		
		for price in prices:
			interest = 0
			next_price =  prices.filter(wdate__gt=price.wdate).first()
			
			if next_price:
				print "------------------------------------------"
				print price.wdate
				print next_price.wdate
				print price.close
				print next_price.close
				interest = (next_price.close - price.close) / price.close

				total_interest += interest
				total_weight += 10

				adj_score = 0
				adj_index = 0
				interest_score = 0
				interest_index = 0
				interest_score_index = 0
			
				try:
					outcome = outcomes.filter(wdate=price.wdate).first()
					print "------------------------------------------"
					print outcome.wdate
					print outcome.DNA_score
					print outcome.DNA_index
					
					adj_score = outcome.adjustScore()
					adj_index = outcome.adjustIndex()
					adj_score_index = (adj_score + adj_index) / 2

					interest_score = (interest * adj_score)/10
					interest_index = (interest * adj_index)/10
					interest_score_index = (interest * adj_score_index) / 10

					total_score += adj_score
					total_index += adj_index
					total_index_score += adj_score_index

					total_interest_index += interest_index
					total_interest_score += interest_score
					total_interest_index_score += interest_score_index

					# intervsinvest_sum = (total_interest * total_weight) /  total_weight
					# intervsinvest_index_sum = (total_interest_index * total_index) / total_weight
					# intervsinvest_score_sum = (total_interest_score * total_score) / total_weight

					intervsinvest_sum = total_interest
					intervsinvest_index_sum = (total_weight / total_index) * total_interest_index
					intervsinvest_score_sum = (total_weight / total_score) * total_interest_score
					intervsinvest_index_score_sum = (total_weight / total_index_score) * total_interest_index_score

					# save backtest result in db
					try:
						log = Log.objects.get(result_id=result.id, wdate=price.wdate)
						log.interest = interest
						log.interest_sum = total_interest
						log.intervsinvest_sum = intervsinvest_sum

						log.index = adj_index
						log.interest_index = interest_index
						log.interest_index_sum = total_interest_index
						log.intervsinvest_index_sum = intervsinvest_index_sum

						log.score = adj_score
						log.interest_score = interest_score
						log.interest_score_sum = total_interest_score
						log.intervsinvest_score_sum = intervsinvest_score_sum

						log.index_score = adj_score_index
						log.interest_index_score = interest_score_index
						log.interest_index_score_sum = total_interest_index_score
						log.intervsinvest_index_score_sum = intervsinvest_index_score_sum

						log.save(update_fields=[
							'interest', 'interest_sum', 'intervsinvest_sum',
							'index', 'interest_index', 'interest_index_sum', 'intervsinvest_index_sum',
							'score', 'interest_score', 'interest_score_sum', 'intervsinvest_score_sum',
							'index_score', 'interest_index_score', 'interest_index_score_sum', 'intervsinvest_index_score_sum'
						])
						print "log updated in db"
					except:
						log = Log(
							result_id = result.id, 
							wdate = price.wdate, 
							interest = interest,
							interest_sum = total_interest,
							intervsinvest_sum = intervsinvest_sum,

							index = adj_index,
							interest_index = interest_index,
							interest_index_sum = total_interest_index,
							intervsinvest_index_sum = intervsinvest_index_sum,

							score = adj_score,
							interest_score = interest_score,
							interest_score_sum = total_interest_score,
							intervsinvest_score_sum = intervsinvest_score_sum,

							index_score = adj_score_index,
							interest_index_score = interest_score_index,
							interest_index_score_sum = total_interest_index_score,
							intervsinvest_index_score_sum = intervsinvest_index_score_sum
						)
						log.save() 
						print "log saved in db"

					cnt = cnt + 1
				except:
					print "outcome related to price doesn't exist"
				
			else:
				print "next price does not exist"
				break

	else:
		print "prices or outcomes does not exist"


def store(request):
	today = datetime.now().strftime("%Y%m%d")
	selected_code = request.POST.get('code-list')
	print selected_code

	s_date = request.POST.get("s_date")
	e_date = request.POST.get("e_date")

	writetocsv(s_date, e_date, selected_code)

	# return HttpResponse("store")
	return HttpResponseRedirect(reverse('insu_index'))

def csv(request, result):
	logs = Log.objects.filter(result=result)
	
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	filename = logs.result.itemcode + '_' + logs.result.start_date + '_' + logs.result.end_date + ".csv"
	response['Content-Disposition'] = 'attachment; filename=' + filename
	writer = csv.writer(response)

	writer.writerow(['코드', '날짜', '투자금액', '일간수익률', '누적 일간수익률', '보유수익률',
									'DNA-리스크 based 비중', '일간수익률', '누적 일간수익률', 'DNA-리스크 based 수익률',
									'DNA-리턴 based 비중', '일간수익률', '누적 일간수익률', 'DNA-리턴 based 수익률',
									'DNA-리턴-리스크 based 평균비중', '일간수익률', '누적 일간수익률', 'DNA-리턴-리스크 based 수익률'
								])

	for log in logs:
		writer.writerow([
									log.result.itemcode, log.wdate, 
									log.weight, log.interest, log.interest_sum, log.intervsinvest_sum,
									log.index, log.interest_index, log.interest_index_sum, log.intervsinvest_index_sum,
									log.score, log.interest_score, log.interest_score_sum, log.intervsinvest_score_sum,
									log.index_score, log.interest_index_score, log.interest_index_score_sum, log.intervsinvest_index_score_sum
								])

	return response