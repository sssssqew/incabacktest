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
	cnt = 0

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

	interest_IVSI = []
	interest_index_IVSI = []
	interest_score_IVSI = []

	ivsi = []

	filename = fname + '.csv'
	filepath = join(settings.MEDIA_ROOT, filename)

	fnames = fname.split('_')
	# print fnames
	code = fnames[1]
	s_date = fnames[2]
	e_date = fnames[4]

	result = Result.objects.get(itemcode=code, start_date=s_date, end_date=e_date)
	print result.id
	# try:
	# 	IVSI = InterVSInvest.objects.get(result_id=result.id)
	# 	print "IVSI exists"
	# except:
	# 	IVSI = InterVSInvest()
	# 	print "IVSI dosen't exists"

	with open(filepath, 'r') as f:
		reader = list(csv.reader(f, delimiter=str(',')))
		for row in reader: 
			if row != reader[-1]:
				date.append(row[1])
				# interest.append(row[3])
				# interest_index.append(row[5])
				# interest_score.append(row[7])
				log = Log.objects.get(result_id=result.id, wdate=row[1])
				# print log.wdate
				# print log.interest_sum
				interest.append(str(log.interest_sum))
				interest_index.append(str(log.interest_index_sum))
				interest_score.append(str(log.interest_score_sum))

				interest_IVSI.append(str(log.intervsinvest_sum))
				interest_index_IVSI.append(str(log.intervsinvest_index_sum))
				interest_score_IVSI.append(str(log.intervsinvest_score_sum))

				#누적수익률 추가 
				row.append(str(log.interest_sum))
				row.append(str(log.interest_index_sum))
				row.append(str(log.interest_score_sum))

				#투자대비 수익률 
				row.append(str(log.intervsinvest_sum))
				row.append(str(log.intervsinvest_index_sum))
				row.append(str(log.intervsinvest_score_sum))
			else:
				iv = Decimal(row[3]) 
				iv_index = Decimal(row[2])/Decimal(row[4])*Decimal(row[5]) 
				iv_score = Decimal(row[2])/Decimal(row[6])*Decimal(row[7]) 
				ivsi.append(iv)
				ivsi.append(iv_index)
				ivsi.append(iv_score)

			rows.append(row)

	date.insert(0, 'x')
	interest.insert(0, '누적 일간수익률')
	interest_index.insert(0, '누적 일간수익률(Index)')
	interest_score.insert(0, '누적 일간수익률(Score)')

	interest_IVSI.insert(0, '보유수익률')
	interest_index_IVSI.insert(0, 'DNA-리스크 based 수익률')
	interest_score_IVSI.insert(0, 'DNA-리턴 based 수익률')

	columns = [date, interest, interest_index, interest_score]
	columns_sum = [date, interest_IVSI, interest_index_IVSI, interest_score_IVSI]
	context = {'columns': json.dumps(columns), 'columns_sum': json.dumps(columns_sum), 'rows':rows, 'IVSI':ivsi}
	return render(request, 'incatest/show.html', context)


def create(request):
	funds = Fund.objects.all()
	context = {'funds':funds}

	return render(request, "incatest/create.html", context)

@background(queue='backtest')
def writetocsv(filepath, prices_ids, result_id):
	prices = Price.objects.filter(id__in=prices_ids)

	total_interest = 0
	total_weight = 0
	total_index = 0
	total_interest_index = 0
	total_score = 0
	total_interest_score = 0

	# 투자대비 수익률 변수 
	intervsinvest = 0
	intervsinvest_index = 0
	intervsinvest_score = 0

	intervsinvest_sum = 0
	intervsinvest_index_sum = 0
	intervsinvest_score_sum = 0

	cnt = 0
	with open(filepath, 'w') as f:
		writer = csv.writer(f, csv.excel)
		for price in prices:
			interest = 0
			next_item =  Price.objects.filter(itemcode=price.itemcode, wdate__gt=price.wdate).order_by('wdate').first()
			current_price = price.getInterest()
			print current_price
			print next_item.close
			interest = (next_item.close - current_price) / current_price
			print interest
			print total_interest
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

				cnt = cnt + 1
			except:
				print "outcome related to price doesn't exist"
			# print price.wdate 
			
			# save backtest result in db
			try:
				intervsinvest_sum = total_interest
				intervsinvest_index_sum = (total_weight / total_index) * total_interest_index
				intervsinvest_score_sum = (total_weight / total_score) * total_interest_score
				log = Log.objects.get(result_id=result_id, wdate=price.wdate)
				log.interest = interest
				log.interest_sum = total_interest
				log.interest_index = interest_index
				log.interest_index_sum = total_interest_index
				log.interest_score = interest_score
				log.interest_score_sum = total_interest_score
				log.intervsinvest_sum = intervsinvest_sum
				log.intervsinvest_index_sum = intervsinvest_index_sum
				log.intervsinvest_score_sum = intervsinvest_score_sum
				log.save(update_fields=['interest', 
							'interest_sum', 'interest_index', 'interest_index_sum', 'interest_score', 'interest_score_sum', 
							'intervsinvest_sum', 'intervsinvest_index_sum', 'intervsinvest_score_sum'])
				print "log updated in db"
			except:
				# intervsinvest_sum = (total_interest * total_weight) /  total_weight
				# intervsinvest_index_sum = (total_interest_index * total_index) / total_weight
				# intervsinvest_score_sum = (total_interest_score * total_score) / total_weight
				intervsinvest_sum = total_interest
				intervsinvest_index_sum = (total_weight / total_index) * total_interest_index
				intervsinvest_score_sum = (total_weight / total_score) * total_interest_score 
				log = Log(
					result_id = result_id, 
					wdate = price.wdate, 
					interest = interest,
					interest_sum = total_interest,
					interest_index = interest_index,
					interest_index_sum = total_interest_index,
					interest_score = interest_score,
					interest_score_sum = total_interest_score,
					intervsinvest_sum = intervsinvest_sum,
					intervsinvest_index_sum = intervsinvest_index_sum,
					intervsinvest_score_sum = intervsinvest_score_sum
				)
				log.save() 
				print "log saved in db"

			# save in file 
			writer.writerow([price.itemcode.encode('euc-kr'), price.wdate, 10, interest, adj_index, interest_index, adj_score, interest_score])

		writer.writerow([price.itemcode.encode('euc-kr'), "Total", total_weight, total_interest, total_index, total_interest_index, total_score, total_interest_score])

		# 투자대비 수익률 계산
		# intervsinvest = (total_interest * total_weight) /  total_weight
		# intervsinvest_index = (total_interest_index * total_index) / total_weight
		# intervsinvest_score = (total_interest_score * total_score) / total_weight

		# intervsinvest = total_interest
		# intervsinvest_index = (Decimal(total_weight) / total_index) * total_interest_index 
		# intervsinvest_score = (Decimal(total_weight) / total_score) * total_interest_score 

		# print total_weight
		# print total_index
		# print total_interest_index
		# print total_score
		# print total_interest_score

		# save backtest result in db
		# try:
		# 	IVSI = InterVSInvest.objects.get(result_id=result_id)
		# 	# IVSI.intervsinvest = intervsinvest
		# 	# IVSI.intervsinvest_index = intervsinvest_index
		# 	# IVSI.intervsinvest_score = intervsinvest_score
		# 	# IVSI.save(update_fields=['intervsinvest', 
		# 	# 				'intervsinvest_index', 'intervsinvest_score'])
		# 	print "IVSI exists in db"
		# except:
		# 	IVSI = InterVSInvest(
		# 		result_id = result_id, 
		# 		intervsinvest = intervsinvest,
		# 		intervsinvest_index = intervsinvest_index,
		# 		intervsinvest_score = intervsinvest_score
		# 	)
		# 	IVSI.save()
		# 	print "IVSI saved in db"

	# print cnt

def store(request):
	today = datetime.now().strftime("%Y%m%d")
	selected_code = request.POST.get('code-list')
	print selected_code

	s_date = request.POST.get("s_date")
	e_date = request.POST.get("e_date")
	# print s_date
	# outcomes = Outcome.objects.filter(itemcode=selected_code, wdate__range=[s_date, e_date])

	# 가격 데이터 없을시 에러처리 필요함 
	try:
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
	except:
		print "price data dosen't exists"
	
	# return HttpResponse("store")
	return HttpResponseRedirect(reverse('insu_index'))