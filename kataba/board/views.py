# -*- coding: utf-8 -*-

# Django modules
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView, ListView, DetailView, View
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.edit import CreateView
from django.utils.html import escape

# Kataba modules
import board
from board.mixins import JsonMixin, JsonFormMixin

# Tags
import simple_tags

# Base class with changed context and dispatcher method (addition attributes - self.board, self.boards).
# Addition argument (board_name) will be taken from url.
class BaseBoardClass(ContextMixin):

    def dispatch(self, *args, **kwargs):
        # Current board. Doing it here because sometimes I need it before get_context_data
        if 'board_name' in kwargs.keys():
            self.board = get_object_or_404(board.models.Board.objects, name=kwargs['board_name'])
        else:
            self.board = None

        return super(BaseBoardClass, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseBoardClass, self).get_context_data(**kwargs)

        # Style
        context['style'] = escape(self.request.COOKIES.get('style', 'style_default.css'))

        context['board'] = self.board
        context['boards'] = board.models.Board.objects.all

        return context

# Class for main page
class IndexView(ListView):

    model = board.models.Board
    template_name = "index.html"
    context_object_name = "boards"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['style'] = escape(self.request.COOKIES.get('style', 'style_default.css'))
        return context

class BoardView(ListView, BaseBoardClass):

    model = board.models.Thread
    template_name = "board.html"
    context_object_name = "threads"
    paginate_by = settings.THREADS

    def get_queryset(self):
        return self.board.get_board_view()

    def get_context_data(self, **kwargs):
        context = super(BoardView, self).get_context_data(**kwargs)

        context['thread_form'] = board.models.ThreadForm()
        return context

class ThreadView(DetailView, BaseBoardClass):

    model = board.models.Thread
    template_name = 'thread.html'
    context_object_name = 'thread'

    def get_context_data(self, **kwargs):
        context = super(ThreadView,self).get_context_data(**kwargs)
        context['post_form'] = board.models.PostForm()
        context['posts'] = board.models.Post.objects.filter(thread_id=context['object'])

        # Hide "Answer" button
        context['thread_hide_answer'] = True
        
        return context

class ThreadAddView(JsonFormMixin, CreateView, BaseBoardClass):

    form_class = board.models.ThreadForm
    model = board.models.Thread

    def form_valid(self, form, send_json=True):
        response = super(ThreadAddView, self).form_valid(form, send_json=False)

        # Addition argument for json answer - url of the new thread.
        response.update(url=reverse('thread_view', args=[self.board.name, self.object.id]))

        # Add tags
        self.object.add_tags(tags=self.request.REQUEST.get('tags', ''))

        return self.render_json_answer(response) if send_json else response

class PostAddView(JsonFormMixin, CreateView, BaseBoardClass):

    form_class = board.models.PostForm
    model = board.models.Post

    def form_valid(self, form, send_json=True):
        # Thread
        current_thread = get_object_or_404(board.models.Thread.objects, id=self.kwargs['thread_id'])

        # Connect thread and future form
        form.instance.thread_id = current_thread

        # Calling original method
        response = super(PostAddView, self).form_valid(form, send_json=False)

        # Updating time of the last post
        if not form.instance.sage and current_thread.post_count < self.board.thread_max_post:
            current_thread.update_time = form.instance.date
            
        # Post count increment
        current_thread.post_count += 1
        current_thread.save()
        
        return self.render_json_answer(response) if send_json else response

class PostView(RedirectView):

    def get_redirect_url(self, pk):
        thread = get_object_or_404(board.models.Post, id=pk).thread_id
        return reverse('thread_view', args=[thread.board_id.name, thread.id])

class ThreadUpdateView(JsonMixin, ListView):

    model = board.models.Post
    template_name = "parts/posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        count = int(self.kwargs['posts_numb'])
        return self.model.objects.filter(thread_id__id=thread_id)[count:]

    def render_to_response(self, context, **kwargs):
        is_new = True if context[self.context_object_name] else False
        response = dict(is_new=is_new)
        if is_new:
            posts = super(ThreadUpdateView, self).render_to_response(context, **kwargs)
            response.update(new_threads=posts.rendered_content)
        return self.render_json_answer(response)

class CloudIndexView(IndexView):

    template_name = 'cloud/index.html'

class CloudView(ListView, BaseBoardClass):

    model = board.models.Thread
    template_name = 'cloud/cloud.html'
    context_object_name = "threads"
    
    def get_queryset(self):
        return self.board.get_cloud_view()

class SingleThreadView(JsonMixin, DetailView):

    model = board.models.Thread
    context_object_name = 'thread'
    template_name = 'parts/thread.html'

    def render_to_response(self, context, **kwargs):
        context.update(thread_hide_answer=True)
        data = super(SingleThreadView, self).render_to_response(context, **kwargs)
        response = dict(answer=data.rendered_content)
        return self.render_json_answer(response)

class SinglePostView(SingleThreadView):

    model = board.models.Post
    context_object_name = 'post'
    template_name = 'parts/post.html'

class SearchView(TemplateView, BaseBoardClass):

    template_name = 'search.html'

    def get_context_data(self, search_text, search_place, search_type, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context.update({
            'threads': board.models.Thread.objects.search(search_text, search_place, self.board) if search_type != 'post' else [],
            'posts': board.models.Post.objects.search(search_text, search_place, self.board) if search_type != 'thread' else [],
            'post_show_answer': True,
            'thread_hide_answer': False,
        })
        return context

class TagView(TemplateView, BaseBoardClass):

    template_name = 'search.html'

    def get_context_data(self, tag, **kwargs):

        tag = get_object_or_404(simple_tags.models.Tag.objects, name=escape(tag))

        context = super(TagView, self).get_context_data(**kwargs)
        context.update({
            'threads': [i.content_object for i in simple_tags.models.TagToTarget.objects.filter(tag=tag)],
            'post_show_answer': True,
            'thread_hide_answer': False,
        })
        return context
