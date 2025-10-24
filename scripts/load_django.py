import sys
import os
import django

sys.path.append('//home')
os.environ['DJANGO_SETTINGS_MODULE'] = 'afr_com.settings'
django.setup()