from django.conf.urls import patterns, url

urlpatterns = patterns('',

	# Index page
	url(r'^$', 'board.views.index', name='index'),
	
	# Board
	url(r'^(?P<boardname>[a-z]{1,3})/(?P<page>[1-9]?)$','board.views.viewboard',name='board'),

	# Thread
	url(r'^thread/(?P<thread_id>[0-9]+)/$','board.views.viewthread',name='viewthread'),

	# Move to post
	url(r'^post/(?P<post_id>[0-9]+)/$','board.views.viewpost',name='viewpost'),

	# Get single post
	url(r'^post/get/(?P<post_id>[0-9]+)/$','board.views.getpost',name='getpost'),

	# Get single thread 
	url(r'^thread/get/(?P<thread_id>[0-9]+)/$','board.views.getthread',name='getpost'),

	# Update thread
	url(r'^thread/update/(?P<thread_id>[0-9]+)/(?P<posts_numb>[0-9]+)$','board.views.updatethread',name='updatethread'),

	# Add post
	url(r'^thread/(?P<thread_id>[0-9]+)/addpost$','board.views.addpost',name='addpost'),

	# Cloud thread vision
	url(r'^(?P<boardname>[a-z]{1,3})/cloud$','board.views.cloud',name='addpost'),
	
	# Search
	url(r'^search/(?P<boardname>([a-z]{1,3}|everywhere))/(?P<search_type>(thread|post|both))/(?P<search_place>(topic|text|both))/(?P<search_text>.+)$','board.views.search',name='addpost'),
	
)
