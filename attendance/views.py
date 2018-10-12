from django.shortcuts import render, redirect
from django.http import HttpResponse
from home.views import loggedInUser
from home.models import Employee
from attendance.models import LeaveType, LeaveRequest
from datetime import date

from home import tests
from datetime import date

def generate_test_data(e):
    tst = tests.HomeTestCase()
    tst.create_in(hours=2, days=1)
    tst.create_out(hours=8, days=1)
    tst.create_in(hours=2, days=6)
    tst.create_out(hours=8, days=6)
    tst.create_in(hours=2, days=7)
    tst.create_out(hours=8, days=7)
    LeaveRequest.objects.create(employee=e, date=date(2018, 10, 4),
                                leaveType=LeaveType.objects.all()[0],
                                description='work at home')
    lv = LeaveRequest.objects.filter(employee=e,
                                    status=LeaveRequest.PENDING)[0]
    lv.approve(e, 'granted')

# Create your views here.
def listAttendance(request):
    user = loggedInUser(request)
    if user:
        #generate_test_data(user)
        context = {'user': user}
        context['absents'] = user.absents(exclude_pending_leaves=True)
        context['leaveTypes'] = LeaveType.objects.all()
        context['leaves'] = user.allLeaves()
        for lt in LeaveType.objects.all():
            context[lt.name] = user.leaves(lt.name)
        return render(request, 'attendance/attendance.html', context=context)
    else:
        return redirect('/login')

def attendance(request):
    if request.method == 'GET':
        return listAttendance(request)
    else:
        user = loggedInUser(request)
        if user:
            lt = request.POST.get('leaveType')
            dates = request.POST.getlist('absents')
            if not dates or lt == 0: return listAttendance(request)
            for _dt in dates:
                dt = list(map(lambda d: int(d), _dt.split('-')))
                pdt = date(dt[0], dt[1], dt[2])
                LeaveRequest.objects.create(employee=user,
                                    date=pdt,
                                    leaveType=LeaveType.objects.get(pk=lt),
                                    description=request.POST.get(_dt))
            return listAttendance(request)
        else:
            return redirect('/login')