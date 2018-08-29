from django.shortcuts import redirect, render

from django.http import HttpResponse
from . import models
from icicle import auth


def home(request):
    if not auth.isLoggedIn(request):
        return redirect('/login')
    else:
        username = request.COOKIES.get('user').split('|')[0]
        user = models.Employee.objects.get(username=username)
        if user.isActive:
            return render(request, 'home.html', context={'user': user})
        else:
            return HttpResponse('Account created for %s!'%user.name +
                                ' Please consult with HR for activation.')
        

def getOrCreateUser(info):
    try:
        user = models.Employee.objects.get(username=auth.makeString(info.get('username')[0]))
    except models.Employee.DoesNotExist:
        
        user = models.Employee(username=auth.makeString(info.get('username')[0]),
#                               dept=info.get('dept')[0],
#                               designation=info.get('designation')[0],
                               name=str(auth.makeString(info.get('name')[0])))
        user.save()
        return None
    else:
        return user