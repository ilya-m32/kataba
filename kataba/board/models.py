#! -*- coding: utf-8 -*-
# Python
import os
import Image
import re

# Django
from django.db import models
from django import forms
from captcha.fields import CaptchaField
from django.conf import settings
from django.utils.html import escape
from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver

class Board(models.Model):
    name = models.CharField(max_length=4)
    pages = models.IntegerField(default=4)
    thread_max_post = models.IntegerField(default=500)

    def get_cloud_view(self):
        # Threads. ("th" 'cause it is shorter)
        threads = Thread.objects.filter(board_id=self).order_by('-update_time')
        
        # How many values should be.
        count = len(threads) + 3 - len(threads) % 3
        
        # Giving back final array
        f = lambda x,y: y[x] if x < len(y) else []
        return [[f(k,threads) for k in xrange(i,i+3)] for i in xrange(0,count,3)]

    def get_board_view(self):
        threads = Thread.objects.filter(board_id=self).order_by('-update_time')
        return [dict(thread=th, posts=th.latest_posts()) for th in threads]
    
    def __unicode__(self):
        return ''.join(['/',self.name,'/'])
        
class SearchManager(models.Manager):
    def search(self,search_text, search_place, board):
        # Making search text safe
        search_text = escape(search_text)
        
        # Where should we search?
        if (search_place == 'topic'):
            query = self.filter(topic__icontains=search_text)
        elif (search_place == 'text'):
            query = self.filter(text__icontains=search_text)
        elif (search_place == 'both'):
            query = self.filter(models.Q(topic__icontains=search_text) | models.Q(text__icontains=search_text))
        
        return query

        
class BasePostModel(models.Model):
    text = models.TextField(max_length=8000)
    topic = models.CharField(max_length=40, blank=False, default=u'Без темы')
    date = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)
    image = models.ImageField(upload_to='.')
    
    # Link to board
    board_id = models.ForeignKey('board')
    
    # Custom Manager
    objects = SearchManager()

    # Delete image and it's thumbnail
    def delete_images(self):
        if self.image:
            images = [''.join([settings.MEDIA_ROOT,'/',self.image.name]),
                      ''.join([settings.MEDIA_ROOT,'/thumbnails/',self.image.name])]
            for image in images:
                if os.path.isfile(image):
                    os.remove(image)    
            

    def make_thumbnail(self):
        """Method which makes thumbnail. Surprise?"""
        if self.image:
            ratio = min(settings.PIC_SIZE/self.image.height,settings.PIC_SIZE/self.image.width)
            thumbnail = Image.open(self.image.path)
            thumbnail.thumbnail((int(self.image.width*ratio),int(self.image.height*ratio)),Image.ANTIALIAS)
            thumbnail.save(''.join([settings.MEDIA_ROOT,'/thumbnails/',self.image.name]),thumbnail.format)
            return True
        else:
            return False
        
    @staticmethod
    def markup(string):
        """ Makes markup for post and thread text. Strings will be safe. """
        string = escape(string)
        markups = [
            # quote
            [r'(?P<text>(?<!(&gt;))&gt;(?!(&gt;)).+)', r'<span class="quote">\g<text></span>'], 
            
            # bold **b**
            [r'\*\*(?P<text>[^*%]+)\*\*' ,r'<b>\g<text></b>'], 
            
            # cursive *i*
            [r'\*(?P<text>[^*%]+)\*', r'<i>\g<text></i>'],
            
            #spoiler %%s%%
            [r'\%\%(?P<text>[^*%]+)\%\%',r'<span class="spoiler">\g<text></span>'],
            
            # link to thread >t14
            [r'\&gt;\&gt;t(?P<id>[0-9]+)',
            r'<div class="link_to_content"><a class="link_to_post" href="/thread/\g<id>">&gt;&gt;t\g<id></a><div class="post_quote"></div></div>'],
            
            # link to post >p88
            [r'\&gt;\&gt;p(?P<id>[0-9]+)',
            r'<div class="link_to_content"><a class="link_to_post" href="/post/\g<id>">&gt;&gt;p\g<id></a><div class="post_quote"></div></div>'], 
            
            # new line
            [r'\n',r'<br>'], 
        ]
        for one_markup in markups:
            string = re.sub(one_markup[0], one_markup[1], string)
        return string
        
    def __unicode__(self):
        return ''.join([self.topic,': ',self.text[:40],', ',str(self.date)])
    
    class Meta:
        abstract = True

class Thread(BasePostModel):
    # Removing old threads
    @classmethod
    def remove_old_threads(cls, board):
        threads_to_delete = cls.objects.filter(board_id=board).order_by('-update_time')[board.pages*settings.THREADS:]
        for th in threads_to_delete:
            th.delete()
    
    def save(self,*args, **kwargs):
        super(Thread,self).save(*args, **kwargs)
        # No more old threads!
        self.remove_old_threads(self.board_id)

    def latest_posts(self,count=3):
        posts = reversed(Post.objects.filter(thread_id=self).order_by('-id')[:count]) # 9,8,7
        return posts

    post_count = models.IntegerField(default=0)
    update_time = models.DateTimeField('%Y-%m-%d %H:%M:%S', auto_now_add=True)

class Post(BasePostModel):        
    thread_id = models.ForeignKey('thread') 
    sage = models.BooleanField(default=False)

class ThreadForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = Thread
        fields = ['topic','text','image']

class PostForm(forms.ModelForm):
    captcha = CaptchaField()
    def __init__(self, *args, **kwargs):
        super(PostForm,self).__init__(*args, **kwargs)
        # Images and sage are not required for posts
        self.fields['image'].required = False
        self.fields['sage'].required = False
        
    class Meta:
        model = Post
        fields = ['topic','sage','text','image']

# Signals

# Use callback to delete images ('cause CASCADE does not call .delete())
@receiver(pre_delete, sender=Thread)
@receiver(pre_delete, sender=Post)
def pre_delete_callback(sender, instance, **kwargs):
    instance.delete_images()

# Callbacks here because save does not always mean new object
@receiver(pre_save, sender=Post)
@receiver(pre_save, sender=Thread)
def pre_save_callback(sender, instance, **kwargs):
    # is it update for something or new object? If it is new, id is None
    if instance.id is None:
        # Topic must be safe
        instance.topic = escape(instance.topic)
        
        # Markup
        instance.text = instance.markup(instance.text)


@receiver(post_save, sender=Thread)
@receiver(post_save, sender=Post)
def post_save_callback(sender, instance, **kwargs):
    if kwargs['created']:
        # Thumbnail
        instance.make_thumbnail()

