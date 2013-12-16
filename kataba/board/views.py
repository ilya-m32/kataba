# -*- coding: utf-8 -*-

# Django modules
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.template import RequestContext, loader
from django.utils.html import escape
from django.db.models import Q

# Python modules
from json import dumps
from os import remove
from time import strftime

# My modules
from board.models import board, post, thread, thread_form, post_form
from board.functions import make_thumbnail,markup

def index(request):
	args = {
		'boards' : board.objects.all()
	}
	return render(request,'index.html', args)

def board_view(request, boardname, page):
	# get all boards
	bd = get_object_or_404(board.objects,name=boardname)
	
	# is there page number?
	if page == '':
		page = 1
	else:
		page = int(page)
		
	# There can't be more pages than db has!
	if page > bd.pages:
		raise Http404
	
	# Add thread
	if request.method == 'POST':
		form = thread_form(request.POST,request.FILES)
		if form.is_valid():
			time = strftime('%Y-%m-%d %H:%M:%S')
			new_thread = thread(
				text=markup(request.POST['text']),
				topic=escape(request.POST['topic']),
				date=time,
				update_time=time,
				board_id=bd,
				image=request.FILES['image'],
			)
			new_thread.save()

			# Making thumbnail
			image = new_thread.image
			make_thumbnail(image,settings)
			
			# Remove old threads
			threads_to_delete = thread.objects.filter(board_id=bd).order_by('update_time').reverse()[bd.pages*settings.THREADS:]
			if threads_to_delete != []:
				for i in threads_to_delete:
					remove(settings.MEDIA_ROOT+'/'+i.image.name)
					remove(settings.MEDIA_ROOT+'/thumbnails/'+i.image.name)
					i.delete()

			return HttpResponseRedirect('/thread/'+str(new_thread.id))
	else:
		form = thread_form()
	
	# Getting threads
	threads = thread.objects.filter(board_id=bd).order_by('update_time').reverse()[settings.THREADS*(page-1):settings.THREADS*page]
	
	threads_numb = len(threads)
	thread_containter = [{} for i in xrange(threads_numb)]
	
	# adding 3 posts there and forming massive with dict.
	for i in xrange(threads_numb):
		thread_containter[i]['thread'] = threads[i]
		thread_containter[i]['posts'] = post.objects.filter(thread_id=threads[i].id).order_by('id').reverse()[:3]

	args = {
		'boardname':boardname,
		'boards':board.objects.all(),
		'show_answer_thread':True,
		'show_answer_post':False,
		'threads':thread_containter,
		'page':page,
		'pages':range(1,bd.pages+1),
		'addthread':form.as_table()
	}
	
	return render(request,'board.html', args)
	
def thread_view(request,thread_id):
	th = get_object_or_404(thread.objects,id=thread_id)
	bd = th.board_id
	boardname = th.board_id.name

	# form
	form = post_form()
	
	threads = {}
	
	posts = post.objects.filter(thread_id=thread_id)
	
	args = {
		'boardname':boardname,
		'boards':board.objects.all(),
		'thread':th,
		'posts': posts,
		'addpost':form.as_table()
	}
	return render(request,'thread.html', args)

def post_view(request,post_id):
	# Thread id
	thread_id = get_object_or_404(post.objects,id=post_id).thread_id.id
	url = '/thread/'+str(thread_id)+'/#p'+str(post_id)
	return HttpResponseRedirect(url)
	
def thread_update(request,thread_id, posts_numb):	
	# All post from thread which are not in thread yet
	posts = post.objects.filter(thread_id=thread_id)[posts_numb:]
	
	answer = {
		'is_new':0,
		'new_threads':""
	}
	
	if len(posts):
		answer['is_new'] = 1 # there IS new posts
		answer['new_threads'] = loader.get_template('parts/posts.html').render(RequestContext(request,{'posts':posts})) # rendered html
	
	return HttpResponse(dumps(answer),content_type="application/json")
	
def post_add(request,thread_id):
	if request.method == 'POST':
		form = post_form(request.POST,request.FILES)
		
		answer = {
			'success':False,
			'form':form.as_table()
		}
		
		if form.is_valid():
			
			# Get thread object
			th = get_object_or_404(thread.objects,id=thread_id)
			
			# Get board object
			bd = th.board_id
			
			# Sage?
			if 'sage' in request.POST.keys():
				sage_val = 1
			else:
				sage_val = 0
				
			# Is there image?
			if 'image' in request.FILES.keys():
				image = request.FILES['image']
			else:
				image = None
			
			# Current time
			time = strftime('%Y-%m-%d %H:%M:%S')
			
			# adding & saving new field	
			new_post = post(
				text= markup(request.POST['text']),
				topic = escape(request.POST['topic']),
				date = time,
				thread_id = th,
				board_id = bd,
				image = image,
				sage = sage_val
			)
			new_post.save()
			
			# updating thread update time
			if ((not sage_val) and (th.post_count < 500)):
				th.update_time = time
			
			# Post count incrementation
			th.post_count = th.post_count+1
			
			# Save changes
			th.save()
			
			# Making thumbnail if there is an image
			if (image):
				image = new_post.image
				make_thumbnail(image,settings)
			
			answer['success'] = True
				
		return HttpResponse(dumps(answer),content_type="application/json")
		
def cloud(request,boardname):
	bd = get_object_or_404(board.objects,name=boardname)
	threads = list(thread.objects.filter(board_id=bd).order_by('update_time').reverse())
	
	threads_len = len(threads)

	# Threads number mod 3 must be = 0
	for i in xrange(3-(threads_len % 3)):
		threads.append([])
	
	# Forming massive for cloud
	threads = [[threads[i],threads[i+1],threads[i+2]] for i in xrange(0,len(threads),3)]
	
	args = {
		'boardname':bd.name,
		'boards':board.objects.all(),
		'threads':threads,
	}
	return render(request,'cloud/cloud.html',args)
	
def cloud_index(request):
	args = {
		'boards' : board.objects.all()
	}
	return render(request,'cloud/index.html', args)
	
def post_get(request,post_id):
	posts = {
		'post': get_object_or_404(post.objects,id=post_id)
	}
	answer = {
		'answer':loader.get_template('parts/post.html').render(RequestContext(request,posts))
	}
	return HttpResponse(dumps(answer),content_type="application/json")
	
def thread_get(request,thread_id):
	threads = {
		'thread':get_object_or_404(thread.objects,id=thread_id)
	}
	answer = {
		'answer':loader.get_template('parts/thread.html').render(RequestContext(request,threads))
	} 
	return HttpResponse(dumps(answer),content_type="application/json")

def search(request,boardname,search_type,search_place,search_text):
	
	# Making text safe
	search_text = escape(search_text)
	
	if (boardname != 'everywhere'):
		bd = get_object_or_404(board.objects,name=boardname)
	else:
		bd = False
	
	args = {
		'boards': board.objects.all(),
		'threads': [],
		'posts': [],
		'show_answer_thread':True,
		'show_answer_post':True,
	}
	
	# Searching for threads
	if (search_type == 'thread' or search_type == 'both'):
		# We search within one board
		if (bd):
			query = thread.objects.filter(board_id=bd)
		else:
			query = thread.objects
		
		if (search_place == 'topic'):
			query = query.filter(topic__icontains=search_text)
		elif (search_place == 'text'):
			query = query.filter(text__icontains=search_text)
		elif (search_place == 'both'):
			query = query.filter(Q(topic__icontains=search_text) | Q(text__icontains=search_text))

		# Add results to the final dict.	
		args['threads'].extend(query)
	
	# Searching for posts
	if (search_type == 'post' or search_type == 'both'):
		# We search within one board
		if (bd):
			query = post.objects.filter(board_id=bd)
		else:
			query = post.objects
		
		if (search_place == 'topic'):
			query = query.filter(topic__icontains=search_text)
		elif (search_place == 'text'):
			query = query.filter(text__icontains=search_text)
		elif (search_place == 'both'):
			query = query.filter(Q(topic__icontains=search_text) | Q(text__icontains=search_text))
		
		# Add results to the final dict.	
		args['posts'].extend(query)

	return render(request,'search.html',args)
