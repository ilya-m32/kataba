#! -*- coding: utf-8 -*-
from django.db import models
from django import forms
from captcha.fields import CaptchaField
from django.conf import settings
from re import sub
from django.utils.html import escape
import os
import Image

class board(models.Model):
	name = models.CharField(max_length=4)
	pages = models.IntegerField(default=4)
	
	def __unicode__(self):
		return ''.join(['/',self.name,'/'])
		
class SearchManager(models.Manager):
	def search(self,search_text,search_place='topic',board=False):
		
		# Search only within one board?
		if (board):
			query = self.filter(board_id=board)
		else:
			query = self
		
		# Where should we search?
		if (search_place == 'topic'):
			query = query.filter(topic__icontains=search_text)
		elif (search_place == 'text'):
			query = query.filter(text__icontains=search_text)
		elif (search_place == 'both'):
			query = query.filter(models.Q(topic__icontains=search_text) | models.Q(text__icontains=search_text))
		
		return query
		
class base_post_model(models.Model):
	text = models.TextField(max_length=8000)
	topic = models.CharField(max_length=40,blank=False,default=u'Без темы')
	date = models.DateTimeField('%Y-%m-%d %H:%M:%S',auto_now=False)
	board_id = models.ForeignKey('board')
	image = models.ImageField(upload_to='.')
	
	# Custom Manager
	objects = SearchManager()
	
	# Delete method which also removes image and its thumbnail
	def delete(self,*args,**kwargs):
		""" Rewrited version which also deletes images and thumbnails """
		if (self.image):
			os.remove(''.join([settings.MEDIA_ROOT,'/',self.image.name]))
			os.remove(''.join([settings.MEDIA_ROOT,'/thumbnails/',self.image.name]))
		super(base_post_model,self).delete(*args,**kwargs)
	
	# Method which makes thumbnail. Surprise?
	def make_thumbnail(self):
		ratio = min(settings.PIC_SIZE/self.image.height,settings.PIC_SIZE/self.image.width)
		thumbnail = Image.open(self.image.path)
		thumbnail.thumbnail((int(self.image.width*ratio),int(self.image.height*ratio)),Image.ANTIALIAS)
		thumbnail.save(''.join([settings.MEDIA_ROOT,'/thumbnails/',self.image.name]),thumbnail.format)
		

	def markup(self, string):
		""" Makes markup for post and thread text. Strings will be safe. """
		string = escape(string)
		markups = [
			[r'(?P<text>(?<!(&gt;))&gt;(?!(&gt;)).+)',r'<span class="quote">\g<text></span>'], # quote
			[r'\*\*(?P<text>[^*%]+)\*\*',r'<b>\g<text></b>'], #bold **b**
			[r'\*(?P<text>[^*%]+)\*',r'<i>\g<text></i>'], #cursive *i*
			[r'\%\%(?P<text>[^*%]+)\%\%',r'<span class="spoiler">\g<text></span>'], #spoiler %%s%%
			[r'\&gt;\&gt;t(?P<id>[0-9]+)',r'<div class="link_to_content"><a class="link_to_post" href="/thread/\g<id>">&gt;&gt;t\g<id></a><div class="post_quote"></div></div>'], # link to thread >t14
			[r'\&gt;\&gt;p(?P<id>[0-9]+)',r'<div class="link_to_content"><a class="link_to_post" href="/post/\g<id>">&gt;&gt;p\g<id></a><div class="post_quote"></div></div>'], # link to post >p88
			[r'\n',r'<br>'], # new line
		]
		for i in markups:
			string = sub(i[0],i[1],string)
		return string

	def save(self,*args,**kwargs):
		
		# Making tumbnail
		if self.image:
			make_thumbnail()
		
		# Markup
		self.text = self.markup(self.text)
		
		# Calling original save method
		super(base_post_model,self).save(*args,**kwargs)
		
	def __unicode__(self):
		return ''.join([self.topic,': ',self.text[:40],', ',str(self.date)])
	
	class Meta:
		abstract = True

class thread(base_post_model):
	def __init__(self,*args,**kwargs):
		super(thread,self).__init__(*args,**kwargs)

	def remove_old(self):
		board = self.board_id
		threads_to_delete = self.objects.filter(board_id=board).order_by('update_time').reverse()[self.board.pages*settings.THREADS:]
		for i in threads_to_delete:
			i.delete()

	post_count = models.IntegerField(default=0)
	update_time = models.DateTimeField('%Y-%m-%d %H:%M:%S',auto_now=False)

class post(base_post_model):
	def __init__(self,*args,**kwargs):
		super(post,self).__init__(*args,**kwargs)
	
	thread_id = models.ForeignKey('thread')	
	sage = models.BooleanField(default=False)

# Forms
class thread_form(forms.Form):
	topic = forms.CharField(
		max_length = 40,
		required = True,
		label = u'Тема',
		widget = forms.TextInput(
			attrs = {
				'size':'30',
				'value':u'Без темы'
			}
		)
	)
	text = forms.CharField(
		widget = forms.Textarea(
			attrs = {'cols':'42'}
		),
		max_length = 8000,
		required = True,
		label = u'Текст',
		error_messages = {
			'required': u'Вы ничего не написали в сообщении'
		}
	)
	
	image = forms.ImageField(
		required = True,
		label = u'Изображение',
		error_messages = {
			'required':u'Для треда нужна пикча.',
			'invalid_image':u'Неверный формат изображения!'
		}
	)
	
	captcha = CaptchaField()

class post_form(thread_form):
	def __init__(self,*args,**kwargs):
		super(post_form,self).__init__(*args,**kwargs)
		self.fields.keyOrder = [
            'topic',
            'sage',
            'text',
            'image',
            'captcha'
		]
		
		# Images are not required for posts
		self.fields['image'].required = False
	
	# Post can have sage
	sage = forms.BooleanField(required=False)
