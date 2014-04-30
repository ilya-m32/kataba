from django.conf.urls import patterns, url
from board import views

urlpatterns = patterns('',

    # Index page
    url(r'^$', views.IndexView.as_view(), name='index'),
    
    # Board
    url(r'^(?P<board_name>[a-z]{1,3})/(?P<page>[1-9]?)$',views.BoardView.as_view(),name='board_view'),

    # Thread
    url(r'^(?P<board_name>[a-z]{1,3})/thread/(?P<pk>[0-9]+)/$',views.ThreadView.as_view(),name='thread_view'),

    # Add thread
    url(r'^(?P<board_name>[a-z]{1,3})/add_thread',views.ThreadAddView.as_view(),name='thread_add'),

    # Move to post
    url(r'^post/(?P<pk>[0-9]+)/$',views.PostView.as_view(),name='post_view'),

    # Get single post
    url(r'^post/get/(?P<pk>[0-9]+)/$',views.SinglePostView.as_view(),name='post_get'),

    # Get single thread 
    url(r'^thread/get/(?P<pk>[0-9]+)/$',views.SingleThreadView.as_view(),name='thread_get'),

    # Update thread
    url(r'^(?P<board_name>[a-z]{1,3})/thread/update/(?P<thread_id>[0-9]+)/(?P<posts_numb>[0-9]+)$',views.ThreadUpdateView.as_view(),name='thread_update'),

    # Add post
    url(r'^(?P<board_name>[a-z]{1,3})/thread/(?P<thread_id>[0-9]+)/add_post$',views.PostAddView.as_view(),name='post_add'),

    # Cloud
    url(r'^cloud/$',views.CloudIndexView.as_view(),name='cloud_index'),

    # Cloud main page
    url(r'^(?P<board_name>[a-z]{1,3})/cloud/$',views.CloudView.as_view(),name='cloud'),
    
    # Search
    url(r'^search/(?P<board_name>([a-z]{1,3}))/(?P<search_type>(thread|post|both))/(?P<search_place>(topic|text|both))/(?P<search_text>.+)$',views.SearchView.as_view(),name='search'),
    
    # All by tag
    url(r'^tag/(?P<tag>(.+))/$', views.TagView.as_view()), 
)
