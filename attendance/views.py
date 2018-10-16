from django.shortcuts import render, redirect
from django.http import HttpResponse
from home.views import loggedInUser
from home.models import Employee
from attendance.models import LeaveType, LeaveRequest, Attendance
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
def listAttendance(request, errors=None):
    user = loggedInUser(request)
    if user:
        year = request.GET.get('year', None)
        if year:
            year = int(year)
        else: year = date.today().year
        #generate_test_data(user)
        context = {'user': user}
        if errors: context['errors'] = errors
        context['year'] = year
        # filter results for specified year
        context['absents'] = user.absents(exclude_pending_leaves=True
                                          ).filter(date__year=year)
        context['leaves'] = user.allLeaves().filter(date__year=year)
        
        context['leaveTypes'] = LeaveType.objects.filter(availability__in=[
                                                    user.currentType()])
        # list of years from first attendance's year to current year
        context['years'] = list(reversed([year for year in range(
                            Attendance.objects.all(
                            ).values_list('date', flat=True).order_by('date'
                            ).first().year, date.today().year + 1)]))
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
            errors = []
            lt = request.POST.get('leaveType')
            dates = request.POST.getlist('absents')
            if not dates or lt == 0: return listAttendance(request)
            lt = LeaveType.objects.get(pk=lt)
            if len(dates) + user.availedLeaves(lt.name,
                                    request.POST.get('year')) > lt.quota:
                errors.append('Number of leave(s) requested exceeded the'+
                              ' allowed quota for selected leave type')
            if errors:
                return listAttendance(request, errors)
            for _dt in dates:
                dt = list(map(lambda d: int(d), _dt.split('-')))
                pdt = date(dt[0], dt[1], dt[2])
                LeaveRequest.objects.create(employee=user,
                                    date=pdt,
                                    leaveType=lt,
                                    description=request.POST.get(_dt))
            return listAttendance(request)
        else:
            return redirect('/login')

def advance_leave(request):
    user = loggedInUser(request)
    if user:
        context = {'user': user}
        if request.method == 'GET':
            return render(request, 'attendance/advance_leave.html', context=context)
        else:
            pass