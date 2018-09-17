'''
Created on Aug 13, 2018

@author: qurban.ali
'''
from django.shortcuts import render, redirect
from django.http import HttpResponse
from home.views import getOrCreateUser
from . import auth
import json
import re



def home(request):
    if not auth.isLoggedIn(request):
        return redirect('/login')
    else:
        return redirect('/home')

def showLoginForm(request, errors=None):
    return render(request, 'login.html', context={'errors': errors})

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
                userInfo = auth.authenticate(username, password)
                if userInfo is None:
                    errors.append('Invalid Username or Password')
                else:
                    userInfo = userInfo[0][1]
                    age = None
                    if request.POST.get('rememberMe') == 'on':
                        age = 365 * 24 * 60 * 60 # one year
                    if getOrCreateUser({'username': auth.makeString(
                                            userInfo['sAMAccountName'][0]),
                                        'name': auth.makeString(
                                            userInfo['name'][0])}) is None:
                        path = '/home'
                    else:
                        path = request.META.get('redirect_path', '/home') #TODO: not possible (how to add path to POST?)
                    response = redirect(path)
                    response.set_cookie('user',
                               auth.makeSecureCookie(username),
                               max_age=age)
                    return response
        else:
            if not username: errors.append('Username missing')
            if not password: errors.append('Password missing')
        if errors:
            return showLoginForm(request, errors)
        
def logout(request):
    if auth.isLoggedIn(request):
        response = redirect('/login')
        response.delete_cookie('user')
        return response
    else:
        return HttpResponse('You are not logged in.')

