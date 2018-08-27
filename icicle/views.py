'''
Created on Aug 13, 2018

@author: qurban.ali
'''
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .ad_auth import authenticate
import json


def home(request):
    if not isLoggedIn():
        redirect('login/')
    
def isLoggedIn():
    pass

def login(request):
    if not isLoggedIn():
        return render(request, 'templates/login.html')
    else:
        pass
        
        