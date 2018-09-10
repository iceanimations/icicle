'''
Created on Sep 6, 2018

@author: qurban.ali
'''
import re

def isalnumud(info):
    return re.match('^[A-Za-z0-9_\.]$')