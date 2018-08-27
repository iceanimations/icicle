'''
Created on Aug 16, 2018

@author: qurban.ali
'''
from django.urls import path
from . import views

urlpatterns = [
               path('', views.home)
]