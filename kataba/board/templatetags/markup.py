from re import sub
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

def markup(string):
	string = escape(string)

	markups = [
		 # new line
		[r'(?P<text>(?<!(&gt;))&gt;(?!(&gt;)).+)',r'<span class="quote">\g<text></span>'], # quote
		[r'\*\*(?P<text>[^*%]+)\*\*',r'<b>\g<text></b>'], #bold **b**
		[r'\*(?P<text>[^*%]+)\*',r'<i>\g<text></i>'], #cursive *i*
		[r'\%\%(?P<text>[^*%]+)\%\%',r'<span class="spoiler">\g<text></span>'], #spoiler %%s%%
		[r'\&gt;\&gt;t(?P<id>[0-9]+)',r'<div class="link_to_content"><a class="link_to_post" href="/thread/\g<id>">&gt;&gt;t\g<id></a><div class="post_quote"></div></div>'], # link to thread >t14
		[r'\&gt;\&gt;p(?P<id>[0-9]+)',r'<div class="link_to_content"><a class="link_to_post" href="/post/\g<id>">&gt;&gt;p\g<id></a><div class="post_quote"></div></div>'], # link to post >p88
		[r'\n',r'<br>'],
	]
	
	for i in xrange(len(markups)):
		string = sub(markups[i][0],markups[i][1],string)

	string = mark_safe(string)
	return string

# Adding mine filter
register = template.Library()
register.filter('markup',markup)

