# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import datetime

class LeaveType(models.Model):
    SICK_LEAVE = 'sickLeave'
    CASUAL_LEAVE = 'casualLeave'
    ANUAL_LEAVE = 'anualLeave'
    OFFICIAL_LEAVE = 'officialLeave'
    SPECIAL_LEAVE = 'specialLeave'
    HAJJ_LEAVE = 'hajjLeave'
    MARRIAGE_LEAVE = 'marriageLeave'
    EMERGENCY_LEAVE = 'emergencyLeave'
    UNPAID_LEAVE = 'unpaidLeave'
    
    LEAVE_NAME_CHOICES = ((SICK_LEAVE, 'Sick Leave'),
                          (CASUAL_LEAVE, 'Casual Leave'),
                          (ANUAL_LEAVE, 'Anual Leave'),
                          (OFFICIAL_LEAVE, 'Official Leave'),
                          (SPECIAL_LEAVE, 'Special Leave'),
                          (HAJJ_LEAVE, 'Hajj Leave'),
                          (MARRIAGE_LEAVE, 'Marriage Leave'),
                          (EMERGENCY_LEAVE, 'Emergency Leave'),
                          (UNPAID_LEAVE, 'Unpaid Leave'))

    name = models.CharField(max_length=20, choices=LEAVE_NAME_CHOICES)
    quotaMax = models.IntegerField(verbose_name='Quota (Max per Year)')
    consecutiveMax = models.IntegerField(verbose_name='Consecutive (Max)')
    consecutiveMin = models.IntegerField(verbose_name='Consecutive (Min)')
    caryForwardable = models.BooleanField(verbose_name='Carry Forwardable')
    onceOnly = models.BooleanField(verbose_name='Once per Employee')
    periodForAdvance = models.IntegerField(verbose_name='Advance Application Period (Days)')
    availability = models.ManyToManyField('home.EmployeeType')
    
    def __str__(self):
        for name, nicename in self.LEAVE_NAME_CHOICES:
            if name == self.name: return nicename

class Attendance(models.Model):
    GRACE_TIME = 0
    
    PRESENT = 'present'
    ABSENT = 'absent'
    HOLIDAY = 'holiday'
    WEEKEND = 'weekend'
    
    STATUS_CHOICES = ((PRESENT, 'Present'),
                      (ABSENT, 'Absent'),
                      (HOLIDAY, 'Holiday'),
                      (WEEKEND, 'Weekend')) + LeaveType.LEAVE_NAME_CHOICES
    
    date = models.DateField(auto_now_add=True)
    employee = models.ForeignKey('home.Employee', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20)
    isLate = models.BooleanField(verbose_name='Is Late?', default=False)
    isHalfDay = models.BooleanField(verbose_name='Is a Half Day?', default=False)
    isShortDay = models.BooleanField(verbose_name='Is a Shot Day?', default=False)
    
    def __str__(self):
        return str(self.date) + ' - ' + self.employee.name
    
    @classmethod
    def markAttendance(cls, employee, intime):
        Attendance(employee=employee, status=cls.PRESENT,
                         isLate=intime.time() <= employee.shift.timeFrom + cls.GRACE_TIME).save()

class LeaveRequest(models.Model):
    attendance = models.ForeignKey(Attendance, null=True, blank=True, on_delete=models.SET_NULL)
    leaveType = models.ForeignKey(LeaveType, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    approvalDate = models.DateTimeField()
    approvedBy = models.ForeignKey('home.Employee', null=True, blank=True, on_delete=models.SET_NULL)
    remarks = models.TextField(blank=True)
    
    def __str__(self):
        return self.attendance.employee.name +' - '+ str(self.attendance.date)

class Day(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self, *args):
        return self.name

class Weekend(models.Model):
    name = models.CharField(max_length=20)
    days = models.ManyToManyField(Day, through='DayOfWeekend')
    
    def __str__(self):
        return self.name

class DayOfWeekend(models.Model):
    weekend = models.ForeignKey(Weekend, null=True, blank=True, on_delete=models.SET_NULL)
    day = models.ForeignKey(Day, null=True, blank=True, on_delete=models.SET_NULL)

class Shift(models.Model):
    name = models.CharField(max_length=30)
    weekend = models.ForeignKey(Weekend, null=True, blank=True, on_delete=models.SET_NULL)
    timeFrom = models.TimeField()
    timeTo = models.TimeField()
    
    def __str__(self):
        return self.name
    
class Ramzan(models.Model):
    dateFrom = models.DateField(verbose_name='Starts From')
    dateTo = models.DateField(verbose_name='Ends On', null=True, blank=True)
    
    @classmethod
    def isRamzan(cls, date=None):
        if date is None:
            date = datetime.date.today()
        for obj in cls.objects.all():
            if obj.dateTo is None:
                obj.dateTo = obj.dateFrom + datetime.timedelta(days=30)
                 
            if date >= obj.dateFrom and date <= obj.dateTo:
                return True
        return False
    
    def __str__(self):
        return str(self.dateFrom) +' - '+ str(self.dateTo)

class Holiday(models.Model):
    name = models.CharField(max_length=30)
    date = models.DateField()
    
    def __str__(self):
        return self.name +' - '+ str(self.date)

class InOut(models.Model):
    BIOMETRIC = 'biometric'
    MANUAL = 'manual'
    COMPUTED = 'computed'
    SELF = 'self'
    
    IN = 'in'
    OUT = 'out'
    
    INOUT_TYPE_CHOICES = ((BIOMETRIC, 'Biometric'),
                          (MANUAL, 'Manual'),
                          (COMPUTED, 'Computed'),
                          (SELF, 'Self'))
    
    STATUS_CHOICES = ((IN, 'In'), (OUT, 'Out'))
    
    employee = models.ForeignKey('home.Employee', null=True, blank=True, on_delete=models.SET_NULL)
    inoutId = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)
    inoutType = models.CharField(choices=INOUT_TYPE_CHOICES, max_length=15, default=BIOMETRIC)
    status = models.CharField(choices=STATUS_CHOICES, max_length=15)
    
    def __str__(self):
        return self.employee.name +' - '+ self.status +' - '+ str(self.datetime)
    
    def lastInoutId(self, employee=None):
        ids = self.objects.values_list('inoutId', flat=True)
        if len(ids) > 0:
            m = max(ids); c = ids.count(m)
        else:
            m = 0; c = 1
        return m, c
    
    def save(self, *args, **kwargs):
        lastId = self.lastInoutId()
        if lastId != 0:
            eLastId = self.objects.filter(employee=self.employee).aggregate(models.Max('inoutId'))
            eLastStatus = self.objects.filter(inoutId=eLastId)
            if len(eLastStatus) == 2:
                eLastStatus = self.OUT
            else: eLastStatus = self.IN
            if self.status == eLastStatus:
                return
        else:
            if self.status == self.OUT:
                return
        if self.status == self.IN:
            self.inoutId = lastId + 1
        else: self.inoutId = lastId
        super(InOut, self).save(*args, **kwargs)
        if self.status == self.IN:
            today = datetime.datetime.today()
            now = self.employee.shift.timeFrom
            ins = self.objects.filter(employee=self.employee,
                                      datetime__gt=datetime.datetime(today.year, today.month, today.day, now.hour, now.minute, now.second),
                                      datetime__lt=self.datetime,
                                      status=self.IN)
            if len(ins) == 0:
                Attendance.markAttendance(self.employee, self.datetime)