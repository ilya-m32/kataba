from django.conf.urls import patterns, url
import views

urlpatterns = patterns('simple_tags.views',

	url(r'^complete/(?P<tag>((\w)|[0-9% ])+)/(?P<limit>[0-9]*)/$', views.CompleteTagAjaxView, name='find'),

)