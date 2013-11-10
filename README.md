kataba
======
Imageboard engine written with Python and Django.
Written for Django >=1.4  and Python 2.x
It uses following modules:
1) PIL or Pillow for making thumbnails
2) Django simple captcha (for captcha obviously)
3) Any database you prefer (f.e. sqlite3 or MySQL)

How to install:
1) Edit kataba/local_settings_example.py and rename it to local_settings.py
2) Create a database: ./manage.py syncdb
3) Add boards in your_url/admin and use!
