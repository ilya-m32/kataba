
from re import sub
from django.utils.html import escape


def markup(string):
	"""
		Makes markup for post and thread text. Strings will be safe.
	"""
	
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
