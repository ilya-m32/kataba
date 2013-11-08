# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from board.models import board, post, thread, addthread, addpost
from time import strftime
from django.conf import settings
from django.template import RequestContext, loader
from json import dumps
import Image


def index(request):
	args = {'boards':board.objects.all()}
	return render(request,'index.html', args)

def viewboard(request, boardname, page):
	bd = get_object_or_404(board.objects,name=boardname)
	
	# is there page number?
	try:
		type(page)
	except NameError:
		page = 1
		
	if page == '':
		page = 1
	else:
		page = int(page)
		
	# There can't be more pages than db has!
	if page > bd.pages:
		raise Http404
	
	# Add thread
	if request.method == 'POST':
		thread_form = addthread(request.POST,request.FILES)
		if thread_form.is_valid():
			new_thread = thread(text=request.POST['text'],topic=request.POST['topic'],date=strftime('%Y-%m-%d %H:%M:%S'),board_id=bd,image=request.FILES['image'])
			new_thread.save()

			# Making thumbnail
			image = new_thread.image
			
			ratio = min(settings.PIC_SIZE/image.height,settings.PIC_SIZE/image.width)
			thumbnail = Image.open(image.path)
			thumbnail.thumbnail((int(image.width*ratio),int(image.height*ratio)),Image.ANTIALIAS)
			thumbnail.save(settings.MEDIA_ROOT+'/thumbnails/'+image.name,thumbnail.format)
			
			return HttpResponseRedirect('/thread/'+str(new_thread.id))
			
	else:
		thread_form = addthread()
	
	# Getting threads
	op_posts = thread.objects.filter(board_id=bd).order_by('update_time').reverse()[8*(page-1):8*page]
	
	posts_numb = len(op_posts)
	threads = [{} for i in xrange(posts_numb)]
	# adding 3 posts there and forming massive with dict.
	for i in xrange(0,posts_numb):
		threads[i]['op'] = op_posts[i]
		threads[i]['other'] = list(post.objects.filter(thread_id=op_posts[i].id))[-3:]
		
	args = {'boardname':boardname, 'boards':board.objects.all(), 'threads':threads, 'page':page,'pages':range(1,bd.pages+1), 'addthread':thread_form.as_table()}
	return render(request,'board.html', args)
	
def viewthread(request,thread_id):
	th = get_object_or_404(thread.objects,id=thread_id)
	bd = th.board_id
	boardname = th.board_id.name
	
	# Add post
	if request.method == 'POST':
		post_form = addpost(request.POST,request.FILES)
		if post_form.is_valid():
			if 'sage' in request.POST.keys():
				sage_val = 1
			else:
				sage_val = 0
			if 'image' in request.FILES.keys():
				image = request.FILES['image']
			else:
				image = None
			
			# Current time
			time = strftime('%Y-%m-%d %H:%M:%S')
			
			# adding & saving new field	
			new_post = post(text=request.POST['text'],board_id=bd,topic=request.POST['topic'],date=time,thread_id=th,image=image,sage=sage_val)
			new_post.save()
			
			# updating thread update_time
			if not sage_val:
				th.update_time = time
				th.save()
				
			# Making thumbnail if there is an image
			
			if image:
				image = new_post.image
				ratio = min(settings.PIC_SIZE/image.height,settings.PIC_SIZE/image.width)
				thumbnail = Image.open(image.path)
				thumbnail.thumbnail((int(image.width*ratio),int(image.height*ratio)),Image.ANTIALIAS)
				thumbnail.save(settings.MEDIA_ROOT+'/thumbnails/'+image.name,thumbnail.format)

			# redirect to the new thread
			return HttpResponseRedirect('/thread/'+str(thread_id))
	else:
		post_form = addpost()
		
	posts = post.objects.filter(thread_id=thread_id)
	args = {'boardname':boardname, 'boards':board.objects.all(), 'thread':th, 'posts':posts, 'addpost':post_form.as_table()}
	return render(request,'thread.html', args)

def viewpost(request,post_id):
	return HttpResponseRedirect('/thread/'+str(get_object_or_404(post.objects,id=post_id).thread_id.id)+'/#p'+str(post_id))
	
def updatethread(request):
	if request.method != 'POST':
		return HttpResponseRedirect('/')
	
	if ('thread_id' not in request.POST.keys()) or 'posts_numb' not in request.POST.keys():
		raise Http404
	else:
		thread_id = int(request.POST['thread_id'])
		posts_numb = int(request.POST['posts_numb'])
	
	posts = post.objects.filter(thread_id=thread_id)
	posts = posts[posts_numb:]
	if len(posts) > 0:
		is_new = 1
		template = loader.get_template('posts.html').render(RequestContext(request,{'posts':posts}))
	else:
		is_new = 0
		template = ''
	return HttpResponse(dumps({'is_new':is_new,'new_threads':template}),content_type="application/json")
	
