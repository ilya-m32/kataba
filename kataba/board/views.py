# -*- coding: utf-8 -*-

# Python modules
import json
import time
import pprint

# Django modules
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.template import RequestContext, loader
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, ListView, DetailView

# Kataba module
from board import models

class IndexView(ListView):
    model = models.Board
    template_name = "index.html"
    context_object_name = "boards"

class BoardView(ListView):
    model = models.Thread
    template_name = "board.html"
    context_object_name = "threads"
    paginate_by = settings.THREADS

    # Replaced dispatch method with declaration of new attr with board object.
    def dispatch(self, *args, **kwargs):
        self.board = get_object_or_404(models.Board.objects,name=kwargs['name'])
        return super(BoardView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        threads = self.model.objects.filter(board_id=self.board).order_by('update_time').reverse()

        thread_container = [{} for i in xrange(len(threads))]
        
        for i in xrange(len(threads)):
            thread_container[i]['thread'] = threads[i]
            thread_container[i]['posts'] = models.Post.objects.filter(thread_id=threads[i].id).order_by('id').reverse()[:3]
        return thread_container

    def get_context_data(self,**kwargs):
        context = super(BoardView,self).get_context_data(**kwargs)
        context['board'] = self.board
        context['thread_form'] = models.ThreadForm()
        return context

    ## Add thread
    #if request.method == 'POST':
        #form = models.ThreadForm(request.POST,request.FILES)
        #if form.is_valid():
            #current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            #new_thread = models.Thread(
                #text=request.POST['text'],
                #topic=request.POST['topic'],
                #date=current_time,
                #update_time=current_time,
                #board_id=board,
                #image=request.FILES['image'],
            #)
            
            ## Saving new thread
            #new_thread.save()
            
            #return HttpResponseRedirect(reverse('thread_view',args=[new_thread.id]))
    #else:
        #form = models.ThreadForm()
class ThreadView(DetailView):
    model = models.Thread
    template_name = "thread.html"
    context_object_name = 'thread'

    def get_context_data(self,**kwargs):
        context = super(ThreadView,self).get_context_data(**kwargs)
        context['post_form'] = models.PostForm()
        context['posts'] = models.Post.objects.filter(thread_id=context['object'])
        return context

def post_view(request,post_id):
    # Thread id
    thread_id = get_object_or_404(models.Post.objects,id=post_id).thread_id.id
    return HttpResponseRedirect(reverse('thread_view',args=[thread_id]))
    
def thread_update(request,thread_id, posts_numb):   
    # All post from thread which are not in thread yet
    posts = models.Post.objects.filter(thread_id=thread_id)[posts_numb:]
    
    answer = {
        'is_new':0,
        'new_threads':""
    }
    
    if posts:
        answer['is_new'] = 1 # there IS new posts
        answer['new_threads'] = loader.get_template('parts/posts.html').render(RequestContext(request,{'posts':posts})) # rendered html
    
    return HttpResponse(json.dumps(answer),content_type="application/json")

@require_POST
def post_add(request,thread_id):
    form = models.PostForm(request.POST,request.FILES)
    
    answer = {
        'success':False,
        'form':form.as_table()
    }
    
    if form.is_valid():
        
        # Get thread object
        thread = get_object_or_404(models.Thread.objects,id=thread_id)
        
        # Get board object
        board = thread.board_id
        
        # Sage?
        if 'sage' in request.POST.keys():
            sage_val = 1
        else:
            sage_val = 0
            
        # Is there an image?
        if 'image' in request.FILES.keys():
            image = request.FILES['image']
        else:
            image = None
        
        # Current time
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # adding & saving new field 
        new_post = models.Post(
            text = request.POST['text'],
            topic = request.POST['topic'],
            date = current_time,
            thread_id = thread,
            image = image,
            sage = sage_val,
            board_id = board
        )
        new_post.save()
        
        # Thread changes
        thread.update_time = current_time
        thread.post_count += 1
        
        # Save changes
        thread.save()
        
        answer['success'] = True
            
    return HttpResponse(json.dumps(answer),content_type="application/json")
        
def cloud(request,boardname):
    board = get_object_or_404(models.Board.objects,name=boardname)
    threads = list(models.Thread.objects.filter(board_id=board).order_by('update_time').reverse())

    # Threads number mod 3 must be = 0
    for i in xrange(3-(len(threads) % 3)):
        threads.append([])
    
    # Forming massive for cloud
    threads = [[threads[i],threads[i+1],threads[i+2]] for i in xrange(0,len(threads),3)]
    
    args = {
        'boardname':board.name,
        'boards':models.Board.objects.all(),
        'threads':threads,
    }
    return render(request,'cloud/cloud.html',args)
    
def cloud_index(request):
    args = {
        'boards' : models.Board.objects.all()
    }
    return render(request,'cloud/index.html', args)
    
def post_get(request,post_id):
    args = {
        'post': get_object_or_404(models.Post.objects,id=post_id)
    }
    answer = {
        'answer':loader.get_template('parts/post.html').render(RequestContext(request,args))
    }
    return HttpResponse(json.dumps(answer),content_type="application/json")
    
def thread_get(request,thread_id):
    args = {
        'thread':get_object_or_404(models.Thread.objects,id=thread_id)
    }
    answer = {
        'answer':loader.get_template('parts/thread.html').render(RequestContext(request,args))
    } 
    return HttpResponse(json.dumps(answer),content_type="application/json")

def search(request,boardname,search_type,search_place,search_text): 
    if (boardname != 'everywhere'):
        board = get_object_or_404(models.Board.objects,name=boardname)
    else:
        board = False
    
    args = {
        'boards': models.Board.objects.all(),
        'threads': models.Thread.objects.search(search_text,search_place,board) if search_type != 'post' else [],
        'posts': models.Post.objects.search(search_text,search_place,board) if search_type != 'thread' else [],
        'show_answer_thread':True,
        'show_answer_post':True,
    }

    return render(request,'search.html',args)
