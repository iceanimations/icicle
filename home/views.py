from django.shortcuts import redirect, render

from django.http import HttpResponse
from . import models
from attendance.models import Shift, Weekend, EmployeeWeekend, EmployeeShift
from icicle import auth, utilities as util
import json


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
    username = info.get('username')
    try:
        user = models.Employee.objects.get(username=username)                    
    except models.Employee.DoesNotExist:
        
        user = models.Employee(username=username, name=info.get('name'))
        user.save()
        return None
    else:
        return user
    
def editEmployee(request):
    context = {'employees': models.Employee.objects.all()}
    if request.method == 'POST':
        errors = []
        emp = models.Employee.objects.get(pk=int(request.POST['pk']))
        photo = request.FILES.get('photo', None)
        if photo is not None:
            emp.photo = photo
        isActive = request.POST.get('isActive', None)
        if isActive is None: emp.isActive = False
        else: emp.isActive = True
        code = request.POST.get('code', None)
        if code.isdigit(): emp.code = code
        else: errors.append('Invalid Code')
        name = request.POST.get('name', None)
        if name: emp.name = name
        else: errors.append('Name not found')
        email = request.POST.get('email', None)
        if email: emp.email = email
        username = request.POST.get('username', None)
        if username: emp.username = username
        else: errors.append('Username not found')
        fatherName = request.POST.get('fatherName', None)
        if fatherName: emp.fatherName = fatherName
        else: errors.append('Father\'s name not found')
        address = request.POST.get('address', None)
        if address: emp.address = address
        phone = request.POST.get('phone', None)
        if phone: emp.phone = phone
        mobile = request.POST.get('mobile', None)
        if mobile: emp.mobile = mobile
        else: errors.append('Mobile not found')
        cnic = request.POST.get('cnic', None)
        if cnic: emp.cnic = cnic
        dob = request.POST.get('dob', None)
        if dob: emp.dob = dob
        jd = request.POST.get('joinDate', None)
        if jd: emp.joinDate = jd
        dept = int(request.POST.get('dept'))
        if dept:
            dept = models.Department.objects.get(pk=dept)
            if emp.currentDept() != dept:
                empDept = models.EmployeeDepartment(employee=emp, dept=dept)
                empDept.setLastDeptDateTo()
                empDept.save()
        weekend = int(request.POST.get('weekend'))
        if weekend:
            weekend = Weekend.objects.get(pk=weekend)
            if emp.currentWeekend() != weekend:
                empWeekend = EmployeeWeekend(employee=emp, weekend=weekend)
                empWeekend.setLastWeekendDateTo()
                empWeekend.save()
        shift = int(request.POST.get('shift'))
        if shift:
            shift = Shift.objects.get(pk=shift)
            if emp.currentShift() != shift:
                empShift = EmployeeShift(employee=emp, shift=shift)
                empShift.setLastShiftDateTo()
                empShift.save()
        emp.save()
        return render(request, 'home/employee_edit.html', context=context)
    else:
        pk = request.GET.get('pk', '')
        if pk:
            pk = int(pk)
            context['departments'] = models.Department.objects.all()
            context['shifts'] = Shift.objects.all()
            context['designations'] = models.Designation.objects.all()
            context['types'] = models.EmployeeType.objects.all()
            context['weekends'] = Weekend.objects.all()
            context['employee'] = models.Employee.objects.get(pk=pk)
        return render(request, 'home/employee_edit.html', context=context)