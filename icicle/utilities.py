'''
Created on Sep 6, 2018

@author: qurban.ali
'''
import re
from django.utils import timezone

def isalnumud(info):
    return re.match('^[A-Za-z0-9_\.]$')

def utcToLocalTime(utc):
    return timezone.localtime(utc)