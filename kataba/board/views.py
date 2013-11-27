# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from board.models import board, post, thread, addthread_form, addpost_form
from time import strftime
from django.conf import settings
from django.template import RequestContext, loader
from json import dumps
from board_functions import make_thumbnail


def index(request):
	args = {'boards':board.objects.all()}
	return render(request,'index.html', args)

def viewboard(request, boardname, page):
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
		thread_form = addthread_form(request.POST,request.FILES)
		if thread_form.is_valid():
			new_thread = thread(
				text=request.POST['text'],
				topic=request.POST['topic'],
				date=strftime('%Y-%m-%d %H:%M:%S'),
				board_id=bd,image=request.FILES['image']
			)
			new_thread.save()

			# Making thumbnail
			image = new_thread.image
			make_thumbnail(image,settings)

			return HttpResponseRedirect('/thread/'+str(new_thread.id))
			
	else:
		thread_form = addthread_form()
	
	# Getting threads
	op_posts = thread.objects.filter(board_id=bd).order_by('update_time').reverse()[settings.THREADS*(page-1):settings.THREADS*page]
	
	posts_numb = len(op_posts)
	threads = [{} for i in xrange(posts_numb)]
	# adding 3 posts there and forming massive with dict.
	for i in xrange(0,posts_numb):
		threads[i]['thread'] = op_posts[i]
		threads[i]['posts'] = list(post.objects.filter(thread_id=op_posts[i].id).reverse())[-3:]
		
	args = {
		'boardname':boardname,
		'boards':board.objects.all(),
		'threads':threads,
		'page':page,
		'pages':range(1,bd.pages+1),
		'addthread':thread_form.as_table()
	}
	
	return render(request,'board.html', args)
	
def viewthread(request,thread_id):
	th = get_object_or_404(thread.objects,id=thread_id)
	bd = th.board_id
	boardname = th.board_id.name

	# form
	post_form = addpost_form()
	
	threads = {}
	
	threads['thread'] = th
	threads['posts'] = post.objects.filter(thread_id=thread_id)
	
	args = {
		'boardname':boardname,
		'boards':board.objects.all(),
		'thread':threads,
		'addpost':post_form.as_table()
	}
	return render(request,'thread.html', args)

def viewpost(request,post_id):
	return HttpResponseRedirect('/thread/'+str(get_object_or_404(post.objects,id=post_id).thread_id.id)+'/#p'+str(post_id))
	
def updatethread(request,thread_id, posts_numb):	
	posts = post.objects.filter(thread_id=thread_id)
	posts = posts[posts_numb:]
	if len(posts):
		is_new = 1 # there IS new posts
		template = loader.get_template('parts/posts.html').render(RequestContext(request,{'thread':{'posts':posts}})) # rendered html
	else:
		is_new = 0 # and there is no...
		template = '' # nothing because there is nothing to render
	return HttpResponse(dumps({'is_new':is_new,'new_threads':template}),content_type="application/json")
	
def addpost(request,thread_id):
	if request.method == 'POST':
		post_form = addpost_form(request.POST,request.FILES)
		if post_form.is_valid():
			
			# Get thread Object
			th = get_object_or_404(thread.objects,id=thread_id)
			
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
				text=request.POST['text'],
				topic=request.POST['topic'],
				date=time,
				thread_id=th,
				image=image,
				sage=sage_val
			)
			new_post.save()
			
			# updating thread update_time
			if not sage_val and th.post_count < 500:
				th.update_time = time
			
			# Post count incrementation
			th.post_count = th.post_count+1
			
			# Save changes
			th.save()
				
			if image:
				image = new_post.image
				# Making thumbnail if there is an image
				make_thumbnail(image,settings)
		else:
			return HttpResponse(dumps({'success':False,'form':post_form.as_table()}),content_type="application/json")
		return HttpResponse(dumps({'success':True,'form':post_form.as_table()}),content_type="application/json")
		
def cloud(request,boardname):
	bd = get_object_or_404(board.objects,name=boardname)
	threads = list(thread.objects.filter(board_id=bd).order_by('update_time').reverse())
	if len(threads) % 3 != 0:
		for i in xrange(0,(len(threads) % 3)-1):
			threads.append([])
	threads = [[threads[i],threads[i+1],threads[i+2]] for i in range(0,len(threads),3)]
	args = {
		'boardname':bd.name,
		'boards':board.objects.all(),
		'threads':threads,
	}
	return render(request,'cloud.html',args)
