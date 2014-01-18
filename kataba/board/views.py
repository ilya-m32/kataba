# -*- coding: utf-8 -*-

# Django modules
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView, ListView, DetailView, View
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.edit import CreateView

# Kataba modules
from board import models
from board.mixins import JsonMixin, JsonFormMixin

# Base class with changed context and dispatcher method (addition attributes - self.board, self.boards).
# Addition argument (board_name) will be taken from url.
class BaseBoardClass(ContextMixin):
    def dispatch(self, *args, **kwargs):
        # Current board
        self.board = get_object_or_404(models.Board.objects,name=kwargs['board_name']) if 'board_name' in kwargs.keys() else None
        
        # All boards
        self.boards = models.Board.objects.all
        return super(BaseBoardClass, self).dispatch(*args, **kwargs)

    def get_context_data(self,**kwargs):
        context = super(BaseBoardClass,self).get_context_data(**kwargs)
        context['board'] = self.board
        context['boards'] = self.boards
        return context

# Class for main page
class IndexView(ListView):
    model = models.Board
    template_name = "index.html"
    context_object_name = "boards"

class BoardView(ListView,BaseBoardClass):
    model = models.Thread
    template_name = "board.html"
    context_object_name = "threads"
    paginate_by = settings.THREADS

    def get_queryset(self):
        threads = self.model.objects.filter(board_id=self.board).order_by('update_time').reverse()

        thread_container = [{} for i in xrange(len(threads))]
        
        for i in xrange(len(threads)):
            thread_container[i]['thread'] = threads[i]
            thread_container[i]['posts'] = list(models.Post.objects.filter(thread_id=threads[i].id))[-3:]
        return thread_container

    def get_context_data(self,**kwargs):
        context = super(BoardView,self).get_context_data(**kwargs)
        context['thread_form'] = models.ThreadForm()
        return context

class ThreadView(DetailView,BaseBoardClass):        
    model = models.Thread
    template_name = 'thread.html'
    context_object_name = 'thread'

    def get_context_data(self,**kwargs):
        context = super(ThreadView,self).get_context_data(**kwargs)
        context['post_form'] = models.PostForm()
        context['posts'] = models.Post.objects.filter(thread_id=context['object'])
        return context

class ThreadAddView(JsonFormMixin,CreateView,BaseBoardClass):
    form_class = models.ThreadForm
    model = models.Thread

    def form_valid(self, form,send_json=True):
        response = super(ThreadAddView,self).form_valid(form,send_json=False)

        # Addition argument for json answer - url of the new thread.
        response.update({
            'url': reverse('thread_view',args=[self.board.name,self.object.id])
        })

        return self.render_json_answer(response) if send_json else response

class PostAddView(JsonFormMixin,CreateView,BaseBoardClass):
    form_class = models.PostForm
    model = models.Post

    def form_valid(self, form,send_json=True):
        # Thread
        current_thread = get_object_or_404(models.Thread.objects,id=self.kwargs['thread_id'])

        # Updating time of the last post
        if not form.instance.sage and current_thread.post_count < self.board.thread_max_post:
            current_thread.update_time = form.instance.date
        current_thread.post_count += 1
        current_thread.save()

        # Connect thread and future form
        form.instance.thread_id = current_thread
        
        response = super(PostAddView,self).form_valid(form,send_json=False)
        return self.render_json_answer(response) if send_json else response

class PostView(RedirectView):
    def get_redirect_url(self,pk):
        thread = get_object_or_404(models.Post,id=pk).thread_id
        return reverse('thread_view',args=[thread.board_id.name,thread.id])

class ThreadUpdateView(JsonMixin,ListView):
    model = models.Post
    template_name = "parts/posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        current_thread = get_object_or_404(models.Thread.objects,id=self.kwargs['thread_id'])
        return self.model.objects.filter(thread_id=current_thread)[int(self.kwargs['posts_numb']):]

    def render_to_response(self,context,**kwargs):
        is_new = True if context[self.context_object_name] else False
        response = {
            'is_new':is_new,
        }
        if is_new:
            posts = super(ThreadUpdateView,self).render_to_response(context,**kwargs)
            response.update({
                'new_threads':posts.rendered_content,
            })
        return self.render_json_answer(response)

class CloudIndexView(IndexView):
    template_name = 'cloud/index.html'

class CloudView(ListView,BaseBoardClass):
    model = models.Thread
    template_name = 'cloud/cloud.html'
    context_object_name = "threads"
    
    def get_queryset(self):
        threads = list(self.model.objects.filter(board_id=self.board).order_by('update_time').reverse())

        # Threads number mod 3 must be = 0
        for i in xrange(3-(len(threads) % 3)):
            threads.append([])
    
        # Returning massive for cloud
        return [[threads[i],threads[i+1],threads[i+2]] for i in xrange(0,len(threads),3)]

class SingleThreadView(JsonMixin,DetailView):
    model = models.Thread
    context_object_name = 'thread'
    template_name = 'parts/thread.html'

    def render_to_response(self,context,**kwargs):
        context['thread_hide_answer'] = True
        data = super(SingleThreadView,self).render_to_response(context,**kwargs)
        response = {
            'answer': data.rendered_content
        }
        return self.render_json_answer(response)

class SinglePostView(SingleThreadView):
    model = models.Post
    context_object_name = 'post'
    template_name = 'parts/post.html'

class SearchView(TemplateView,BaseBoardClass):
    template_name = 'search.html'

    def get_context_data(self,search_text,search_place,search_type, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context.update({
            'threads': models.Thread.objects.search(search_text,search_place,self.board) if search_type != 'post' else [],
            'posts': models.Post.objects.search(search_text,search_place,self.board) if search_type != 'thread' else [],
            'post_show_answer': True,
            'thread_hide_answer': False,
        })
        return context
