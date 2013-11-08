from django.conf.urls import patterns, url

from board import views

urlpatterns = patterns('',
 url(r'^$', views.index, name='index'),
)
