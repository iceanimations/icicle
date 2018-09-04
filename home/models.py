from django.db import models

class EmployeeType(models.Model):
    type = models.CharField(max_length=20, verbose_name='Employee Type')
    
    def __str__(self):
        return self.type
    
class Designation(models.Model):
    title = models.CharField(max_length=30)
    
    def __str__(self):
        return self.title
    
def rename_photo(instance, name):
    return 'home/employee/photo/{}.{}'.format(instance.pk, name.split('.')[-1])

class Employee(models.Model):
    code = models.IntegerField(null=True, blank=True, default='')
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50, null=True, blank=True, default='')
    photo = models.ImageField(upload_to=rename_photo, blank=True, default='') #app/model/field
    username = models.CharField(max_length=50)
    fatherName = models.CharField(max_length=50, verbose_name='Father\'s Name', blank=True, null=True, default='')
    dept = models.ForeignKey('Department', null=True, blank=True, on_delete=models.CASCADE)
    shift = models.ForeignKey('attendance.Shift', null=True, blank=True, on_delete=models.SET_NULL)
    designation = models.ForeignKey(Designation, null=True, blank=True, on_delete=models.SET_NULL)
    dob = models.DateField(verbose_name='Date of Birth', blank=True, null=True, default='')
    joinDate = models.DateField(verbose_name='Joining Date', blank=True, null=True, default='')
    type = models.ForeignKey(EmployeeType, null=True, blank=True, on_delete=models.SET_NULL)
    address = models.CharField(max_length=200, blank=True, null=True, default='')
    isActive = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True, default='')
    mobile = models.CharField(max_length=15, blank=True, null=True, default='')
    cnic = models.CharField(max_length=13, blank=True, null=True, default='')
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