# Just an example of wsgi file
import os, sys

# Path to kataba
KATABA_PATH = os.path.dirname(os.path.realpath(__file__))+'/kataba/'

sys.path.append('/usr/share/pyshared/django')
sys.path.append(KATABA_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'kataba.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
