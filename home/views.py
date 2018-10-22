from django.shortcuts import redirect, render

from django.http import HttpResponse
from . import models
from attendance.models import Shift, EmployeeShift
from icicle import auth, utilities as util
import json
import os
from datetime import date

def home(request):
    try: # deal the situation when user logged in but got deleted from database
        if not auth.isLoggedIn(request):
            return redirect('/login')
        else:
            user = loggedInUser(request)
            if user.isActive():
                return render(request, 'home/home.html', context={'user': user})
            else:
                return HttpResponse('Account created for %s!'%user.name +
                                    ' Please consult HR for activation.')
    except:
        response = redirect('/login')
        response.delete_cookie('user')
        return response
#TODO: remove temp 123 user
def loggedInUser(request):
    if os.environ['USERNAME'] == '123':
        return models.Employee.objects.get(username='qurban.ali')
    cookie = request.COOKIES.get('user')
    if cookie:
        username = cookie.split('|')[0]
        return models.Employee.objects.get(username=username)

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

class EmpTemp(object):
    pass
    
def editEmployee(request):
    user = loggedInUser(request)
    if user:
        context = {'employees': models.Employee.objects.all()}
        context['user'] = user
        context['departments'] = models.Department.objects.all()
        context['shifts'] = Shift.objects.all()
        context['designations'] = models.Designation.objects.all()
        context['types'] = models.EmployeeType.objects.all()
        if request.method == 'POST':
            errors = []
            empTemp = EmpTemp()
            emp = models.Employee.objects.get(pk=int(request.POST['pk']))
            photo = request.FILES.get('photo', None)
            if photo is not None:
                emp.photo = photo
            elif not emp.photo:
                errors.append('Photo missing')
            isActive = bool(request.POST.get('isActive', None))
            code = request.POST.get('code', None)
            dt = None
            jd = request.POST.get('joinDate', None)
            ed = request.POST.get('endDate', None)
            if isActive:
                dt = jd
                if not emp.isActive():
                    if not dt:
                        errors.append('Joining Date missing')
                    if not code:
                        errors.append('Code missing')
                    if not code.isdigit():
                        errors.append('Invalid Code')
            else:
                dt = ed
                if emp.isActive():
                    if not dt:
                        errors.append('Ending Date missing')
            name = request.POST.get('name', None)
            if name: emp.name = name
            else: errors.append('Name missing')
            email = request.POST.get('email', None)
            if email: emp.email = email
            username = request.POST.get('username', None)
            if username: emp.username = username
            else: errors.append('Username missing')
            fatherName = request.POST.get('fatherName', None)
            if fatherName: emp.fatherName = fatherName
            else: errors.append('Father\'s name missing')
            address = request.POST.get('address', None)
            if address: emp.address = address
            phone = request.POST.get('phone', None)
            if phone: emp.phone = phone
            mobile = request.POST.get('mobile', None)
            if mobile: emp.mobile = mobile
            else: errors.append('Mobile missing')
            cnic = request.POST.get('cnic', None)
            if cnic:
                if cnic.isdigit():
                    emp.cnic = cnic
                else:
                    errors.append('Invalid CNIC')
            dob = request.POST.get('dob', None)
            if dob: emp.dob = dob
            dept = int(request.POST.get('dept'))
            fields = [] # fields to save if no error
            if dept:
                dept = models.Department.objects.get(pk=dept)
                if emp.currentDept() != dept:
                    empDept = models.EmployeeDepartment(employee=emp, dept=dept)
                    empDept.setLastDeptDateTo()
                    fields.append(empDept)
            else: errors.append('Department missing')
            shift = int(request.POST.get('shift'))
            if shift:
                shift = Shift.objects.get(pk=shift)
                if emp.currentShift() != shift:
                    empShift = EmployeeShift(employee=emp, shift=shift)
                    empShift.setLastShiftDateTo()
                    empShift.save()
            designation = int(request.POST.get('designation'))
            if designation:
                designation = models.Designation.objects.get(pk=designation)
                if emp.currentDesignation() != designation:
                    empDesignation = models.EmployeeDesignation(employee=emp,
                                                         designation=designation)
                    empDesignation.setLastDesignationDateTo()
                    fields.append(empDesignation)
            else: errors.append('Designation missing')
            typ = int(request.POST.get('type'))
            if typ:
                typ = models.EmployeeType.objects.get(pk=typ)
                if emp.currentType() != typ:
                    empType = models.EmployeeTypeMapping(employee=emp, type=typ)
                    empType.setLastTypeDateTo()
                    fields.append(empType)
            else: errors.append('Type missing')
            if errors:
                #TODO: dates problem
                #return HttpResponse(emp.photoUrl)
                empTemp.photoUrl = emp.photoUrl
                empTemp.name = name
                empTemp.isActive = isActive
                empTemp.code = code
                try:
                    empTemp.joiningDate = date.fromisoformat(jd)
                except ValueError:
                    empTemp.joiningDate = jd
                try:
                    empTemp.endingDate = date.fromisoformat(ed)
                except ValueError:
                    empTemp.endingDate = ed
                empTemp.username = username
                empTemp.email = email
                empTemp.fatherName = fatherName
                empTemp.address = address
                empTemp.mobile = mobile
                empTemp.phone = phone
                empTemp.cnic = cnic
                try:
                    empTemp.dob = date.fromisoformat(dob)
                except ValueError:
                    empTemp.dob = dob
                empTemp.currentDept = dept
                empTemp.currentShift = shift
                empTemp.currentDesignation = designation
                empTemp.currentType = typ
                empTemp.pk = emp.pk
                context['errors'] = errors
                context['employee'] = empTemp
            else:
                for field in fields: field.save()
                if isActive:
                    if not emp.isActive():
                        emp.activate(dt, code)
                else:
                    if emp.isActive():
                        emp.deactivate(dt)
                emp.save()
            return render(request, 'home/employee_edit.html', context=context)
        else:
            pk = request.GET.get('pk', '')
            if pk:
                pk = int(pk)
                context['employee'] = models.Employee.objects.get(pk=pk)
            return render(request, 'home/employee_edit.html', context=context)
    else:
        response = redirect('/login')
        response['redirect_path'] = '/home/editEmployee'
        return response