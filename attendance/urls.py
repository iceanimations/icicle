'''
Created on Aug 17, 2018

@author: qurban.ali
'''
from django.urls import path
from . import views


urlpatterns = [
               path('', views.attendance),
               path('advance/', views.advance_leave),
               path('remove/', views.remove_pending_leave),
               path('approve/', views.approve_leaves)
]
