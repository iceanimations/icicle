from django.shortcuts import render, redirect
from django.http import HttpResponse
from home.views import loggedInUser

# Create your views here.
def attendance(request):
    user = loggedInUser(request)
    if user:
        context = {'user': user}
        return render(request, 'attendance/attendance.html', context=context)
    else:
        return redirect('/login')