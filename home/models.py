from django.db import models
from datetime import date, timedelta
from django.apps import apps

class EmployeeType(models.Model):
    type = models.CharField(max_length=20, verbose_name='Employee Type',
                            unique=True)
    
    def __str__(self):
        return self.type
    
class Designation(models.Model):
    title = models.CharField(max_length=30, unique=True)
    
    def __str__(self):
        return self.title
    
def rename_photo(instance, name):
    return 'home/employee/photo/{}.{}'.format(instance.pk, name.split('.')[-1])

class Employee(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50, null=True, blank=True, unique=True)
    photo = models.ImageField(upload_to=rename_photo, blank=True)
    username = models.CharField(max_length=50, unique=True)
    fatherName = models.CharField(max_length=50, verbose_name='Father\'s Name',
                                  blank=True, null=True)    
    dob = models.DateField(verbose_name='Date of Birth', blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True, unique=True)
    cnic = models.CharField(max_length=13, blank=True, null=True, unique=True)
    
    dept = models.ManyToManyField('Department', through='EmployeeDepartment',
                                  blank=True)
    
    type = models.ForeignKey(EmployeeType, null=True, blank=True,
                             on_delete=models.SET_NULL)
    shift = models.ForeignKey('attendance.Shift', null=True, blank=True,
                              on_delete=models.SET_NULL)
    designation = models.ForeignKey(Designation, null=True, blank=True,
                                    on_delete=models.SET_NULL)
    weekend = models.ForeignKey('attendance.Weekend', null=True, blank=True,
                                on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.name
    
    @property
    def photoUrl(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        
    def currentDept(self):
        empDept = EmployeeDepartment.lastDept(self)
        if empDept: return empDept.dept
        
    def currentWeekend(self):
        empWeekend = apps.get_model('attendance', 'EmployeeWeekend'
                                    ).lastWeekend(self)
        if empWeekend: return empWeekend.weekend
        
    def currentShift(self):
        empShift = apps.get_model('attendance', 'EmployeeShift').lastShift(self)
        if empShift: return empShift.shift
        
    def currentDesignation(self):
        empDesignation = EmployeeDesignation.lastDesignation(self)
        if empDesignation: return empDesignation.designation
        
    def currentType(self):
        empType = EmployeeTypeMapping.lastType(self)
        if empType: return empType.type
        
    def activate(self, dt, code):
        lastPeriod = self.lastPeriod()
        if lastPeriod:
            if lastPeriod.isActive():
                return
        EmployeePeriod(employee=self, dateFrom=dt, code=code).save()
    
    def deactivate(self, dt):
        lastPeriod = self.lastPeriod()
        if lastPeriod:
            if lastPeriod.isActive():
                lastPeriod.setLastPeriodDateTo(dt)
                lastPeriod.save()
        
    def lastPeriod(self):
        return EmployeePeriod.lastPeriod(self)
        
    def isActive(self):
        lastPeriod = self.lastPeriod()
        if lastPeriod: return lastPeriod.isActive()
        
    def joiningDate(self):
        lastPeriod = self.lastPeriod()
        if lastPeriod:
            return lastPeriod.dateFrom
    
    def endingDate(self):
        lastPeriod = self.lastPeriod()
        if lastPeriod:
            return lastPeriod.dateTo
        
    def code(self):
        lastPeriod = self.lastPeriod()
        if lastPeriod:
            return lastPeriod.code
        

class EmployeePeriod(models.Model):
    employee = models.ForeignKey(Employee, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    dateFrom = models.DateField(verbose_name='From',
                                null=True)
    dateTo = models.DateField(verbose_name='To', blank=True, null=True)
    code = models.IntegerField()
    
    def isActive(self):
        return not bool(self.dateTo)
    
    def setLastPeriodDateTo(self, dt):
        lastPeriod = EmployeePeriod.lastStatus(self.employee)
        if lastPeriod:
            lastPeriod.dateTo = dt
            lastPeriod.save()
    
    @classmethod
    def lastPeriod(cls, emp):
        return cls.objects.filter(employee=emp
                                  ).order_by('dateFrom').last()

class Department(models.Model):
    name = models.CharField(max_length=30, unique=True)
    shift = models.ForeignKey('attendance.Shift', null=True, blank=True,
                              on_delete=models.SET_NULL)
    supervisor = models.ForeignKey(Employee, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL)
    weekend = models.ForeignKey('attendance.Weekend', null=True, blank=True,
                                on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.name
    
class EmployeeDepartment(models.Model):
    employee = models.ForeignKey(Employee, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    dept = models.ForeignKey(Department, null=True, blank=True,
                             on_delete=models.SET_NULL)
    dateFrom = models.DateField(auto_now_add=True, verbose_name='From',
                                null=True)
    dateTo = models.DateField(verbose_name='To', blank=True, null=True)
    
    def setLastDeptDateTo(self):
        lastDept = EmployeeDepartment.lastDept(self.employee)
        if lastDept:
            #stayPeriod = date.today() - lastDept.dateFrom
            #if stayPeriod <= timedelta(days=1):
            if lastDept.dateFrom == date.today():
                lastDept.delete()
            else:
                lastDept.dateTo = date.today() - timedelta(1)
                lastDept.save()
                
    @classmethod
    def lastDept(cls, emp):
        return EmployeeDepartment.objects.filter(employee=emp
                                        ).order_by('dateFrom').last()
        
    def __str__(self):
        return '|'.join([self.employee.name, self.dept.name])
    
class EmployeeDesignation(models.Model):
    employee = models.ForeignKey(Employee, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    designation = models.ForeignKey(Designation, null=True, blank=True,
                                    on_delete=models.SET_NULL)
    dateFrom = models.DateField(auto_now_add=True, verbose_name='From',
                                null=True)
    dateTo = models.DateField(verbose_name='To', blank=True, null=True)
    
    def setLastDesignationDateTo(self):
        lastDesignation = EmployeeDesignation.lastDesignation(self.employee)
        if lastDesignation:
            if lastDesignation.dateFrom == date.today():
                lastDesignation.delete()
            else:
                lastDesignation.dateTo = date.today() - timedelta(1)
                lastDesignation.save()
    
    @classmethod
    def lastDesignation(cls, emp):
        return EmployeeDesignation.objects.filter(employee=emp
                                                  ).order_by('dateFrom').last()
                                                  
class EmployeeTypeMapping(models.Model):
    employee = models.ForeignKey(Employee, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    type = models.ForeignKey(EmployeeType, null=True, blank=True,
                             on_delete=models.SET_NULL)
    dateFrom = models.DateField(auto_now_add=True, verbose_name='From',
                                null=True)
    dateTo = models.DateField(verbose_name='To', blank=True, null=True)
    
    def setLastTypeDateTo(self):
        lastType = EmployeeTypeMapping.lastType(self.employee)
        if lastType:
            if lastType.dateFrom == date.today():
                lastType.delete()
            else:
                lastType.dateTo = date.today() - timedelta(1)
                lastType.save()
                
    @classmethod
    def lastType(cls, emp):
        return EmployeeTypeMapping.objects.filter(employee=emp
                                                  ).order_by('dateFrom').last()
    
class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    dateStart = models.DateField(verbose_name='Start Date')
    dateEnd = models.DateField(null=True, blank=True, verbose_name='End Date')
    active = models.BooleanField()
    manager = models.ForeignKey(Employee, null=True, blank=True,
                                on_delete=models.SET_NULL)
    thumb = models.ImageField(blank=True, verbose_name='Thumbnail')
    
    def __str__(self):
        return self.name