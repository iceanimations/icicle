from django.shortcuts import render, redirect
from . import models
from home.views import loggedInUser
from home.models import Project

def home(request):
    user = loggedInUser(request)
    if user:
        context = {'user': user}
        context['foods'] = models.Food.objects.filter(isActive=True)
        context['projects'] = Project.objects.filter(active=True)
        if request.method == "GET":
            return render(request, 'foodOrder/order.html', context)
        else:
            food = request.POST.get('food')
            project = request.POST.get('project')
            food = models.Food.objects.get(pk=food)
            project = Project.objects.get(pk=project)
            #models.FoodOrder.objects.get(employee=user, food=food, project=project)
            return render(request, 'foodOrder/order.html', context)
    else:
        return redirect('/login')