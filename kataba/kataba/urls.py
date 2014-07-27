from django.conf.urls import patterns, include, url

# Admin
from django.contrib import admin
from board import models

# Settings

admin.autodiscover()
admin.site.register([models.Post, models.Thread, models.Board])


urlpatterns = patterns('',
    # Main module
    url(r'^',include('board.urls')),
    
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    
    # Captcha
    url(r'^captcha/', include('captcha.urls')),

    # Tags
    url(r'^tags/', include('simple_tags.urls')),
)

# Static and media files for development server
from django.conf import settings

# Static and media
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.conf.urls.static import static

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)