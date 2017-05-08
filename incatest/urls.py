# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

# url order is very important 
urlpatterns = [
	url(r'^$', views.index, name='home'),
	url(r'^back-tests/create/$', views.create, name='insu_create'),
	url(r'^back-tests/store/$', views.store, name='insu_store'),
]