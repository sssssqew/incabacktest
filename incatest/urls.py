# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

# url order is very important 
urlpatterns = [
	url(r'^$', views.index, name='home'),
	# url(r'^index/$', views.index, name='incatest_index'),
]