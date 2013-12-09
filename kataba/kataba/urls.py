from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Admin
from django.contrib import admin
from board.models import post, board, thread

admin.autodiscover()
admin.site.register([post, thread, board])


urlpatterns = patterns('',
	# Main module
	url(r'^',include('board.urls')),
	
	# Admin
	url(r'^admin/', include(admin.site.urls)),
	
	# Captcha
	url(r'^captcha/', include('captcha.urls')),
)

# Images
urlpatterns += static('images', document_root='images/')
