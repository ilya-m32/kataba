#! -*- coding: utf-8 -*-
from django.db import models
from django import forms
from captcha.fields import CaptchaField

class board(models.Model):
	name = models.CharField(max_length=4)
	pages = models.IntegerField(default=4)
	def __unicode__(self):
		return '/'+self.name+'/'
	
class thread(models.Model):
	text = models.TextField(max_length=8000)
	topic = models.CharField(max_length=40,blank=False,default=u'Без темы')
	date = models.DateTimeField('%Y-%m-%d %H:%M:%S',auto_now=False)
	board_id = models.ForeignKey('board')
	update_time = models.DateTimeField('%Y-%m-%d %H:%M:%S',auto_now=False)
	image = models.ImageField(upload_to='.',blank=False)
	post_count = models.IntegerField(default=0)
	
	def __unicode__(self):
		return self.topic+': '+self.text[:40]+', '+str(self.date)
	
class post(models.Model):
	text = models.TextField(max_length=8000)
	topic = models.CharField(max_length=40,blank=False,default=u'Без темы')
	sage = models.BooleanField(default=False)
	date = models.DateTimeField('%Y-%m-%d %H:%M:%S',auto_now=True)
	thread_id = models.ForeignKey('thread')
	board_id = models.ForeignKey('board')
	image = models.ImageField(upload_to='.',blank=True)
	
	
	def __unicode__(self):
		return self.topic+': '+self.text[:40]+', '+str(self.date)

# Forms
class addthread_form(forms.Form):
	topic = forms.CharField(max_length=40,required=True,label=u'Тема',widget=forms.TextInput(attrs={'size':'30','value':u'Без темы'}))
	text = forms.CharField(widget=forms.Textarea(attrs={'cols':'42'}),max_length=8000,required=True,label=u'Текст',error_messages={'required': u'Вы ничего не написали в сообщении'})
	image = forms.ImageField(required=True,label=u'Изображение',error_messages={'required':u'Для треда нужна пикча.','invalid_image':u'Неверный формат изображения!'})
	captcha = CaptchaField()

class addpost_form(forms.Form):	
	topic = forms.CharField(max_length=40,required=True,label=u'Тема',widget=forms.TextInput(attrs={'size':'30','value':u'Без темы'}))
	sage = forms.BooleanField(required=False)
	text = forms.CharField(widget=forms.Textarea(attrs={'cols':'42'}),max_length=8000,required=True,label=u'Текст',error_messages={'required': u'Вы ничего не написали в сообщении'})
	image = forms.ImageField(required=False,label=u'Изображение',error_messages={'invalid_image':u'Неверный формат изображения!'})
	captcha = CaptchaField()
