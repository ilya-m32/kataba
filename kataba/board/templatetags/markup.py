from re import sub
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

def markup(string):
	string = escape(string)

	markups = [
		[r'(?P<text>\&gt;.+)\n',r'<span class="quote">\g<text></span>\n'], # quote >text
		[r'\n',r'<br>'], # new line
		[r'\*\*(?P<text>[^*%]+)\*\*',r'<b>\g<text></b>'], #bold **b**
		[r'\*(?P<text>[^*%]+)\*',r'<i>\g<text></i>'], #cursive *i*
		[r'\%\%(?P<text>[^*%]+)\%\%',r'<span class="spoiler">\g<text></span>'], #spoiler %%s%%
		[r'\&gt;\&gt;t(?P<id>[0-9]+)',r'<a href="/thread/\g<id>">&gt;&gt;t\g<id></a>'], # link to thread >t14
		[r'\&gt;\&gt;p(?P<id>[0-9]+)',r'<a href="/post/\g<id>">&gt;&gt;p\g<id></a>'], # link to post >p88
	]
	
	for i in xrange(len(markups)):
		string = sub(markups[i][0],markups[i][1],string)

	string = mark_safe(string)
	return string

# Adding mine filter
register = template.Library()
register.filter('markup',markup)

