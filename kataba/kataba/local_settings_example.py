# Example of local settings
# Should be renamed to local_settings.py
DJANGO_DIR='/home/user/Django/kataba' # path to dir with project

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'kataba_db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

PIC_SIZE = 180.0 # Must be float!

TIME_ZONE = 'Asia/Yekaterinburg'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''
