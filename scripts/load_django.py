import sys
import os
import django

sys.path.append('django-image-uploader')
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_images.settings'
django.setup()