# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import incaResults

import csv
import json

from datetime import datetime
from datetime import timedelta

# Create your views here.
def index(requesst):
	cnt = 0
	incaRes = incaResults.objects.all()
	for incaRe in incaRes:
		print incaRe.itemcode
		cnt = cnt + 1
	return HttpResponse(cnt)
