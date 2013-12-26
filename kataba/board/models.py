#! -*- coding: utf-8 -*-
from django.db import models
from django import forms
from captcha.fields import CaptchaField
from django.conf import settings
import os

class board(models.Model):
	name = models.CharField(max_length=4)
	pages = models.IntegerField(default=4)
	
	def __unicode__(self):
		return '/'+self.name+'/'
		
class post_template(models.Model):
	text = models.TextField(max_length=8000)
	topic = models.CharField(max_length=40,blank=False,default=u'Без темы')
	date = models.DateTimeField('%Y-%m-%d %H:%M:%S',auto_now=False)
	board_id = models.ForeignKey('board')
	image = models.ImageField(upload_to='.')
	
	def delete(self,using=None):
		""" Rewrited version which also deletes images and thumbnails """
		if (self.image):
			os.remove(settings.MEDIA_ROOT+'/'+self.image.name)
			os.remove(settings.MEDIA_ROOT+'/thumbnails/'+self.image.name)
		super(post_template,self).delete(using)
	
	def __unicode__(self):
		return self.topic+': '+self.text[:40]+', '+str(self.date)
	
	
class thread(post_template):
	def __init__(self,*args,**kwargs):
		super(thread,self).__init__(*args,**kwargs)

	post_count = models.IntegerField(default=0)
	update_time = models.DateTimeField('%Y-%m-%d %H:%M:%S',auto_now=False)

class post(post_template):
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
	
	sage = forms.BooleanField(required=False)

