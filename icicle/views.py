'''
Created on Aug 13, 2018

@author: qurban.ali
'''
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .ad_auth import authenticate
import re


def home(request):
    if not isLoggedIn():
        return redirect('login/')
    
def isLoggedIn():
    return False

def showLoginForm(request, errors=None):
    return render(request, 'templates/login.html', context={'errors': errors})

def login(request):
    errors = []
    if request.method == 'GET':
        return showLoginForm(request)
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            um = re.match('^[a-zA-Z0-9_\.]+$', username)
            if not um:
                errors.append('Invalid Username. Allowed characters: A-Z a-z 0-9 _ .')
            pm = re.match('^[a-zA-Z0-9]+$', password)
            if not pm:
                errors.append('Invalid Password. Allowed charachters: A-Z a-z 0-9')
            if um and pm:
                userInfo = authenticate(username, password)
                if userInfo is None:
                    errors.append('Invalid Username or Password')
                else:
                    userInfo = userInfo[0][1]
                    #TODO: set the cookie and redirect
                    # check for remember me
                    #return HttpResponse(userInfo)
        else:
            if not username: errors.append('Username missing')
            if not password: errors.append('Password missing')
        if errors:
            return showLoginForm(request, errors)
        
            
        
        