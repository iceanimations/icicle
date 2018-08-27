'''
Created on Aug 17, 2018

@author: qurban.ali
'''
from __future__ import unicode_literals
from django.contrib import admin
from .models import Food, FoodOrder

admin.site.register([Food, FoodOrder])
