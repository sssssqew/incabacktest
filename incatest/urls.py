# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

# url order is very important 
urlpatterns = [
	url(r'^back-tests/$', views.index, name='insu_index'),
	url(r'^back-tests/create/$', views.create, name='insu_create'),
	url(r'^back-tests/store/$', views.store, name='insu_store'),
	url(r'^back-tests/(?P<result>.+)/$', views.show, name='insu_show'),
]

urlpatterns += static('/upload/', document_root=settings.MEDIA_ROOT)