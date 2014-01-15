from django.conf.urls import patterns, url
from board import views

urlpatterns = patterns('',

    # Index page
    url(r'^$', views.IndexView.as_view(), name='index'),
    
    # Board
    url(r'^(?P<name>[a-z]{1,4})/(?P<page>[1-9]?)$',views.BoardView.as_view(),name='board_view'),

    # Thread
    url(r'^thread/(?P<pk>[0-9]+)/$',views.ThreadView.as_view(),name='thread_view'),

    # Move to post
    url(r'^post/(?P<post_id>[0-9]+)/$','board.views.post_view',name='post_view'),

    # Get single post
    url(r'^post/get/(?P<post_id>[0-9]+)/$','board.views.post_get',name='post_get'),

    # Get single thread 
    url(r'^thread/get/(?P<thread_id>[0-9]+)/$','board.views.thread_get',name='thread_get'),

    # Update thread
    url(r'^thread/update/(?P<thread_id>[0-9]+)/(?P<posts_numb>[0-9]+)$','board.views.thread_update',name='thread_update'),

    # Add post
    url(r'^thread/(?P<thread_id>[0-9]+)/addpost$','board.views.post_add',name='post_add'),

    # Cloud
    url(r'^cloud/$','board.views.cloud_index',name='cloud_index'),

    # Cloud main page
    url(r'^(?P<boardname>[a-z]{1,3})/cloud/$','board.views.cloud',name='cloud'),
    
    # Search
    url(r'^search/(?P<boardname>([a-z]{1,3}|everywhere))/(?P<search_type>(thread|post|both))/(?P<search_place>(topic|text|both))/(?P<search_text>.+)$','board.views.search',name='addpost'),
    
)
