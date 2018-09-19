'''
Created on Aug 17, 2018

@author: qurban.ali
'''
from django.urls import path
from . import views


urlpatterns = [
               path('', views.attendance)
]