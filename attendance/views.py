from django.shortcuts import render, redirect
from django.http import HttpResponse
from home.views import loggedInUser
from home.models import Employee
from attendance.models import LeaveType, LeaveRequest, Attendance, Holiday
from datetime import date, timedelta

from home import tests

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
def listAttendance(request, errors=None, selected_data=None):
    user = loggedInUser(request)
    if user:
        year = request.GET.get('year', None)
        if year:
            year = int(year)
        elif selected_data and 'selected_year' in selected_data:
            year = selected_data['selected_year']
        else:
            year = date.today().year
        #generate_test_data(user)
        context = {'user': user}
        if errors: context['errors'] = errors
        descriptions = []
        if selected_data:
            context.update(selected_data)
            descriptions[:] = context.pop('descriptions')
        absents = user.absents(exclude_pending_leaves=True
                                          ).filter(date__year=year)
        if not descriptions:
            descriptions = ['' for _ in range(len(absents))]
        context['absents'] = zip(absents, descriptions)
        context['year'] = year
        # filter results for specified year
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
            lt = int(request.POST.get('leaveType'))
            dates = request.POST.getlist('absents')
            if not dates:
                errors.append('No absent selected')
            if lt == 0:
                errors.append('No leave type selected')
            else:
                lt = LeaveType.objects.get(pk=lt)
            #TODO: handle quota for carryfordable leaves
            #current quota + last year remaining quota
            year = request.POST.get('year')
            if dates and lt:
                if len(dates) + user.availedLeaves(lt.name, year) > lt.quota:
                    errors.append('Number of leave(s) requested exceeded the'+
                                  ' allowed quota for selected leave type')
            if errors:
                data = {'descriptions': []}
                if lt: data['selected_lt'] = lt.pk
                data['selected_year'] = year
                if dates: data['selected_absents'] = dates
                for dt in user.absents(exclude_pending_leaves=True
                                       ).filter(date__year=year):
                    dtf = dt.date.strftime('%Y-%m-%d')
                    #TODO: this is not working, fix it
                    data['descriptions'].append(request.POST.get(dtf, ''))
                return listAttendance(request, errors, data)
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
        context['leaveTypes'] = LeaveType.objects.filter(
                                    availability__in=[user.currentType()])
        if request.method == 'GET':
            return render(request, 'attendance/advance_leave.html',
                          context=context)
        else:
            errors = []
            dateFrom = request.POST.get('dateFrom')
            dateTo = request.POST.get('dateTo')
            desc = request.POST.get('description')
            leaveType = int(request.POST.get('leaveType'))
            if dateFrom and dateTo:
                if desc != '':
                    if leaveType != 0:
                        leaveType = LeaveType.objects.get(pk=leaveType)
                        if dateFrom < dateTo:
                            days = dateTo - dateFrom
                            #years may be different!
                            yearFrom = dateFrom.year
                            yearTo = dateTo.year
                            availedLeaves = user.availedLeaves(leaveType.name,
                                                               yearFrom)
                            quota = leaveType.quota
                            if yearTo - yearFrom == 1:
                                availedLeaves += availedLeaves(leaveType.name,
                                                               yearTo)
                                quota *= 2 # double the quota
                                if days > quota - availedLeaves:
                                    errors.append('Number of days selected'+
                                                  ' exceeds the available'+
                                                  ' quota')
                                else:
                                    for day in range(days + 1):
                                        dt = dateFrom + timedelta(day)
                                        if not user.isWeekend(dt,
                                            optional=True) and \
                                            not Holiday.isHoliday(dt) and \
                                            not LeaveRequest.objects.filter(
                                                    employee=user,
                                                    date=dt, status__in=[
                                                    LeaveRequest.APPROVED,
                                                    LeaveRequest.PENDING]):
                                            LeaveRequest.objects.create(
                                                employee=user,
                                                date=dt,
                                                leaveType=leaveType,
                                                description=desc)
                                    return redirect('/attenance')
                            else:
                                errors.append('Too many years selected')
                        else:
                            errors.append('Date To can not be less than From')
                    else:
                        errors.append('Leave Type not selected')
                else:
                    errors.append('No description added')
            else:
                errors.append('Date not specified')
            if errors:
                context['dateFrom'] = dateFrom
                context['dateTo'] = dateTo
                context['leaveType'] = leaveType
                context['desc'] = desc
                context['errors'] = errors
                return render(request, 'attendance/advance_leave.html',
                              context=context)
    else:
        return redirect('/login')