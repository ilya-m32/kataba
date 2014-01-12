# -*- coding: utf-8 -*-

# Django modules
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.template import RequestContext, loader
from django.utils.html import escape


# Python modules
from json import dumps
from os import remove
from time import strftime

# My modules
from board import models

def index(request):
	args = {
		'boards' : models.board.objects.all()
	}
	return render(request,'index.html', args)

def board_view(request, boardname, page):
	# get all boards
	board = get_object_or_404(models.board.objects,name=boardname)
	
	# is there page number?
	if page == '':
		page = 1
	else:
		page = int(page)
		
	# There can't be more pages than db has!
	if page > board.pages:
		raise Http404
	
	# Add thread
	if request.method == 'POST':
		form = models.thread_form(request.POST,request.FILES)
		if form.is_valid():
			time = strftime('%Y-%m-%d %H:%M:%S')
			new_thread = models.thread(
				text=request.POST['text'],
				topic=request.POST['topic'],
				date=time,
				update_time=time,
				board_id=board,
				image=request.FILES['image'],
			)
			new_thread.save()
			
			# Remove old threads

			return HttpResponseRedirect(''.join(['/thread/',str(new_thread.id)]))
	else:
		form = models.thread_form()
	
	# Getting threads
	threads = models.thread.objects.filter(board_id=board).order_by('update_time').reverse()[settings.THREADS*(page-1):settings.THREADS*page]
	
	threads_numb = len(threads)
	thread_containter = [{} for i in xrange(threads_numb)]
	
	# adding 3 posts there and forming massive with dict.
	for i in xrange(threads_numb):
		thread_containter[i]['thread'] = threads[i]
		thread_containter[i]['posts'] = models.post.objects.filter(thread_id=threads[i].id).order_by('id').reverse()[:3]

	args = {
		'boardname':boardname,
		'boards':models.board.objects.all(),
		'show_answer_thread':True,
		'show_answer_post':False,
		'threads':thread_containter,
		'page':page,
		'pages':range(1,board.pages+1),
		'addthread':form.as_table()
	}
	
	return render(request,'board.html', args)
	
def thread_view(request,thread_id):
	thread = get_object_or_404(models.thread.objects,id=thread_id)
	board = thread.board_id
	boardname = board.name

	# form
	form = models.post_form()
	
	threads = {}
	
	posts = models.post.objects.filter(thread_id=thread_id)
	
	args = {
		'boardname':boardname,
		'boards':models.board.objects.all(),
		'thread':thread,
		'posts': posts,
		'addpost':form.as_table()
	}
	return render(request,'thread.html', args)

def post_view(request,post_id):
	# Thread id
	thread_id = get_object_or_404(models.post.objects,id=post_id).thread_id.id
	url = ''.join(['/thread/',str(thread_id),'/#p',str(post_id)])
	return HttpResponseRedirect(url)
	
def thread_update(request,thread_id, posts_numb):	
	# All post from thread which are not in thread yet
	posts = models.post.objects.filter(thread_id=thread_id)[posts_numb:]
	
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
		form = models.post_form(request.POST,request.FILES)
		
		answer = {
			'success':False,
			'form':form.as_table()
		}
		
		if form.is_valid():
			
			# Get thread object
			thread = get_object_or_404(models.thread.objects,id=thread_id)
			
			# Get board object
			board = thread.board_id
			
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
			new_post = models.post(
				text = request.POST['text'],
				topic = request.POST['topic'],
				date = time,
				thread_id = thread,
				board_id = board,
				image = image,
				sage = sage_val
			)
			new_post.save()
			
			# Thread changes
			thread.update_time = time
			thread.post_count += 1
			
			# Save changes
			thread.save()
			
			answer['success'] = True
				
		return HttpResponse(dumps(answer),content_type="application/json")
		
def cloud(request,boardname):
	board = get_object_or_404(models.board.objects,name=boardname)
	threads = list(models.thread.objects.filter(board_id=board).order_by('update_time').reverse())
	
	threads_len = len(threads)

	# Threads number mod 3 must be = 0
	for i in xrange(3-(threads_len % 3)):
		threads.append([])
	
	# Forming massive for cloud
	threads = [[threads[i],threads[i+1],threads[i+2]] for i in xrange(0,len(threads),3)]
	
	args = {
		'boardname':board.name,
		'boards':models.board.objects.all(),
		'threads':threads,
	}
	return render(request,'cloud/cloud.html',args)
	
def cloud_index(request):
	args = {
		'boards' : models.board.objects.all()
	}
	return render(request,'cloud/index.html', args)
	
def post_get(request,post_id):
	args = {
		'post': get_object_or_404(models.post.objects,id=post_id)
	}
	answer = {
		'answer':loader.get_template('parts/post.html').render(RequestContext(request,args))
	}
	return HttpResponse(dumps(answer),content_type="application/json")
	
def thread_get(request,thread_id):
	args = {
		'thread':get_object_or_404(models.thread.objects,id=thread_id)
	}
	answer = {
		'answer':loader.get_template('parts/thread.html').render(RequestContext(request,args))
	} 
	return HttpResponse(dumps(answer),content_type="application/json")

def search(request,boardname,search_type,search_place,search_text):
	# Making text safe
	search_text = escape(search_text)
	
	if (boardname != 'everywhere'):
		board = get_object_or_404(models.board.objects,name=boardname)
	else:
		board = False
	
	args = {
		'boards': models.board.objects.all(),
		'threads': models.thread.objects.search(search_text,search_place,board),
		'posts': models.post.objects.search(search_text,search_place,board),
		'show_answer_thread':True,
		'show_answer_post':True,
	}

	return render(request,'search.html',args)
