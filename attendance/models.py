# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime, date, timedelta
from django.apps import apps
import pytz
from icicle import settings

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
    periodForAdvance = models.IntegerField(
                            verbose_name='Advance Application Period (Days)')
    availability = models.ManyToManyField('home.EmployeeType')
    
    def __str__(self):
        for name, nicename in self.LEAVE_NAME_CHOICES:
            if name == self.name: return nicename

class Attendance(models.Model):
    PRESENT = 'present'
    ABSENT = 'absent'
    HOLIDAY = 'holiday'
    WEEKEND = 'weekend'
    
    date = models.DateField(auto_now_add=True)
    employee = models.ForeignKey('home.Employee', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    status = models.CharField(max_length=20)
    #TODO: get shift on a given day, employee, property or method
    def __str__(self):
        return str(self.date) + ' - ' + self.employee.name
    
    @classmethod
    def markAttendance(cls, employee, status):
        Attendance(employee=employee, status=status).save()

class LeaveRequest(models.Model):
    attendance = models.ForeignKey(Attendance, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    leaveType = models.ForeignKey(LeaveType, null=True, blank=True,
                                  on_delete=models.SET_NULL)
    description = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    approvalDate = models.DateTimeField()
    approvedBy = models.ForeignKey('home.Employee', null=True, blank=True,
                                   on_delete=models.SET_NULL)
    remarks = models.TextField(blank=True)
    
    def __str__(self):
        return self.attendance.employee.name +' - '+ str(self.attendance.date)

class Day(models.Model):
    use_for_related_fields = True
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    
class EmployeeShift(models.Model):
    employee = models.ForeignKey('home.Employee', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    shift = models.ForeignKey('Shift', null=True, blank=True,
                              on_delete=models.SET_NULL)
    dateFrom = models.DateField(auto_now_add=True, null=True,
                                verbose_name='From')
    dateTo = models.DateField(null=True,
                              verbose_name='To')
    def setLastShiftDateTo(self):
        lastShift = EmployeeShift.lastShift(self.employee)
        if lastShift:
            if lastShift.dateFrom == date.today():
                lastShift.delete()
            else:
                lastShift.dateTo = date.today() - timedelta(1)
                lastShift.save()
    
    @classmethod
    def lastShift(cls, emp):
        return EmployeeShift.objects.filter(employee=emp
                                        ).order_by('dateFrom').last()
                                        
class Shift(models.Model):
    #when emp marks attendance AHEAD_PERIOD hours before the shift start time
    
    name = models.CharField(max_length=30)
    days = models.ManyToManyField(Day, through='DayOfShift')
    
    def __str__(self):
        return self.name
    
    def weekend(self, optional=False):
        days = Day.objects.all()
        if not optional:
            return set(days).difference(self.days.all())
        return set(days).difference(
                (sday.day for sday in self.dayofshift_set.filter(
                        status=DayOfShift.ON)))
        
    def timeRange(self, day):
        day = self.dayofshift_set.filter(day__name=day)
        if day:
            return day[0].timeFrom, day[0].timeTo, day[0].isTimeToNextDay
    
class DayOfShift(models.Model):
    use_for_related_fields = True
    ON = 'on'
    OPT = 'opt'
    
    STATUS_CHOICES = ((ON, 'On'),
                      (OPT, 'Optional'))
    
    shift = models.ForeignKey(Shift, null=True, on_delete=models.SET_NULL)
    day = models.ForeignKey(Day, null=True, on_delete=models.SET_NULL)
    timeFrom = models.TimeField(verbose_name='From')
    timeTo = models.TimeField(verbose_name='To')
    # when timeTo crosses day boundary
    isTimeToNextDay = models.BooleanField(verbose_name='Crossing Date?')
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    
class Ramzan(models.Model):
    dateFrom = models.DateField(verbose_name='Starts From')
    dateTo = models.DateField(verbose_name='Ends On', null=True, blank=True)
    
    @classmethod
    def isRamzan(cls, date=None):
        if date is None:
            date = date.today()
        for obj in cls.objects.all():
            if obj.dateTo is None:
                obj.dateTo = obj.dateFrom + timedelta(days=30)
                 
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

class Session(models.Model):
    BIOMETRIC = 'biometric'
    MANUAL = 'manual'
    COMPUTED = 'computed'
    SELF = 'self'
    
    employee = models.ForeignKey('home.Employee', null=True,
                                 on_delete=models.SET_NULL)
    
    inTime = models.DateTimeField(null=True, default=None)
    outTime = models.DateTimeField(null=True, default=None)
    
    inType = models.CharField(max_length=15, blank=True)
    outType = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return (self.employee.name + '(' + str(self.inTime) +
                '-' + str(self.outTime) + ')')
        
    def isComplete(self):
        # returns true if outTime is not None
        return bool(self.outTime)
    
    @classmethod
    def previousSession(cls, employee, dt):
        return cls.objects.filter(employee=employee, inTime__lt=dt
                                  ).order_by('inTime').last()
    
    @classmethod
    def nextSession(cls, employee, dt):
        return cls.objects.filter(employee=employee, inTime__gte=dt
                                  ).order_by('inTime').first()
                                  
    def splitable_save(self):
        # split the session at shift start time
        if self.outTime is None:
            self.save()
            return
        date_counter = self.inTime.date()
        start_times = []
        print(self.inTime, self.outTime)
        print(date_counter, self.outTime.date())
        while date_counter <= self.outTime.date():
            time = self.employee.shiftStartingTime(date_counter.strftime('%A'))
            start_time = datetime(
                     date_counter.year,
                     date_counter.month, date_counter.day,
                     time.hour, time.minute, time.second,
                     tzinfo=pytz.timezone(settings.TIME_ZONE))
            if start_time > self.inTime and start_time < self.outTime:
                start_times.append(start_time)
            date_counter += timedelta(days=1)
        if start_times:
            outTime = self.outTime
            outType = self.outType
            self.outTime = start_times[0] - timedelta(seconds=1)
            self.outType = self.COMPUTED
            self.save()
            if len(start_times) > 1:
                Session(employee=self.employee,
                        inTime=start_times[0],
                        inType=self.COMPUTED,
                        outTime=start_times[1] - timedelta(seconds=1),
                        outType=self.COMPUTED).save()
            Session(employee=self.employee,
                    inTime=start_times[-1],
                    inType=self.COMPUTED,
                    outTime=outTime,
                    outType=outType).save()
            
        
       
    

class Entry(models.Model):
    IN = 'in'
    OUT = 'out'
    TID_TO_INOUT = {
        1: IN,
        2: OUT,
        3: IN,
        4: OUT
    }
    
    uid = models.IntegerField()
    tid = models.IntegerField()
    # add timezone info, if server and user are in diff timezones
    date = models.DateField()
    time = models.TimeField()
    
    @property
    def datetime(self):
        # datebase time is in utc, so add timezone info to self.datetime
        # for comparison with database time
        return datetime(self.date.year,
                        self.date.month,
                        self.date.day,
                        self.time.hour,
                        self.time.minute,
                        self.time.second,
                        tzinfo=pytz.timezone(settings.TIME_ZONE))
    
    @property
    def status(self):
        return self.TID_TO_INOUT[self.tid]
    
    @property
    def employee(self):
        # analyse employeeperiod__code param
        return apps.get_model('home', 'Employee'
                              ).objects.filter(employeeperiod__code=self.uid
                                               ).first()
    
    def save(self, *args, typ=Session.BIOMETRIC, **kwargs):
        if self.employee is None:
            raise ValueError('No Employee')
        if self.tid not in self.TID_TO_INOUT:
            raise ValueError('No TID')
        
        if self.status == self.IN:
            ps = Session.previousSession(self.employee, self.datetime)
            if ps:
                if ps.outTime is None:
                    ps.outTime = self.datetime - timedelta(seconds=1)
                    ps.outType = Session.COMPUTED
                    ps.splitable_save()
                    ns = Session.nextSession(self.employee,
                                             self.datetime)
                    if ns:
                        if ns.inType == Session.COMPUTED:
                            ns.inTime = self.datetime
                            ns.inType = typ
                            ns.splitable_save()
                        else:
                            s = Session(employee=self.employee, inTime=self.datetime,
                                inType=typ)                    
                            s.outTime = ns.inTime - timedelta(seconds=1)
                            s.outType = Session.COMPUTED
                            s.splitable_save()
                    else:
                        Session(employee=self.employee, inTime=self.datetime,
                                inType=typ).splitable_save()
                else:
                    if ps.outTime > self.datetime:
                        Session(employee=self.employee, inTime=self.datetime,
                                inType=typ, outTime=ps.outTime,
                                outType=ps.outType).splitable_save()
                        ps.outTime = self.datetime - timedelta(seconds=1)
                        if ps.outType != Session.COMPUTED:
                            ps.outType = Session.COMPUTED
                        ps.splitable_save()
                    else:
                        ns = Session.nextSession(self.employee, self.datetime)
                        if ns:
                            if ns.inType == Session.COMPUTED:
                                ns.inTime = self.datetime
                                ns.inType = typ
                                ns.splitable_save()
                            else:
                                s = Session(employee=self.employee,
                                            inTime=self.datetime,
                                            inType=typ)
                                
                                s.outTime = ns.inTime - timedelta(seconds=1)
                                s.outType = Session.COMPUTED
                                s.splitable_save()
                        else:
                            Session(employee=self.employee,
                                            inTime=self.datetime,
                                            inType=typ).splitable_save()
                            
                            
            else: # when no previous session exist
                ns = Session.nextSession(self.employee, self.datetime)
                if ns:
                    if ns.inType == Session.COMPUTED:
                        ns.inTime = self.datetime
                        ns.inType = typ
                        ns.splitable_save()
                    else:
                        Session(employee=self.employee, inTime=self.datetime,
                                inType=typ,
                                outTime=ns.inTime - timedelta(seconds=1),
                                outType=Session.COMPUTED).splitable_save()
                else:
                    Session(employee=self.employee, inTime=self.datetime,
                            inType=typ).splitable_save()
        else: # when Entry in out
            ps = Session.previousSession(self.employee, self.datetime)
            if ps:
                if ps.outTime is None or ps.outType == Session.COMPUTED:
                    ps.outTime = self.datetime
                    ps.outType = typ
                    ps.splitable_save()
                else:
                    if ps.outTime < self.datetime:
                        Session(employee=self.employee, outTime=self.datetime,
                                outType=typ,
                                inTime=self.datetime - timedelta(seconds=1),
                                inType=Session.COMPUTED).splitable_save()
                    else:
                        Session(employee=self.employee,
                                inTime=self.datetime + timedelta(seconds=1),
                                inType=Session.COMPUTED,
                                outTime=ps.outTime, outType=ps.outType).splitable_save()
                        ps.outTime = self.datetime
                        ps.outType = typ
                        ps.splitable_save()
            else:
                Session(employee=self.employee, outTime=self.datetime,
                        outType=typ,
                        inTime=self.datetime - timedelta(seconds=1),
                        inType=Session.COMPUTED).splitable_save()
        super(Entry, self).save(*args, **kwargs)