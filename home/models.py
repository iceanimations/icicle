from django.db import models

class EmployeeType(models.Model):
    type = models.CharField(max_length=20, verbose_name='Employee Type')
    
    def __str__(self):
        return self.type
    
class Designation(models.Model):
    title = models.CharField(max_length=30)
    
    def __str__(self):
        return self.title

class Employee(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=50)
    photo = models.ImageField()
    username = models.CharField(max_length=50)
    fatherName = models.CharField(max_length=50, verbose_name='Father\'s Name')
    dept = models.ForeignKey('Department', null=True, blank=True, on_delete=models.CASCADE)
    shift = models.ForeignKey('attendance.Shift', null=True, blank=True, on_delete=models.SET_NULL)
    designation = models.ForeignKey(Designation, null=True, blank=True, on_delete=models.SET_NULL)
    dob = models.DateField(verbose_name='Date of Birth')
    joinDate = models.DateField(verbose_name='Joining Date')
    type = models.ForeignKey(EmployeeType, null=True, blank=True, on_delete=models.SET_NULL)
    address = models.CharField(max_length=200, blank=True)
    isActive = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    cnic = models.CharField(max_length=13, blank=True)
    weekend = models.ForeignKey('attendance.Weekend', null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.name
    
class Department(models.Model):
    name = models.CharField(max_length=30)
    shift = models.ForeignKey('attendance.Shift', null=True, blank=True, on_delete=models.SET_NULL)
    supervisor = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    weekend = models.ForeignKey('attendance.Weekend', null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.name
    
class Project(models.Model):
    name = models.CharField(max_length=50)
    dateStart = models.DateField(verbose_name='Start Date')
    dateEnd = models.DateField(null=True, blank=True, verbose_name='End Date')
    active = models.BooleanField()
    manager = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL)
    thumb = models.ImageField(blank=True, verbose_name='Thumbnail')
    
    def __str__(self):
        return self.name