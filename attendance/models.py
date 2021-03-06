# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.apps import apps
import pytz
from icicle import settings, utilities as utils

#TODO: consider making ForeignKey ManyToManyField whereever possible
#TODO: models optimization through inheritance

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

    name = models.CharField(max_length=20, unique=True)
    quota = models.IntegerField(verbose_name='Quota (Max per Year)')
    caryForwardable = models.BooleanField(verbose_name='Carry Forwardable',
                                          default=False)
    onceOnly = models.BooleanField(verbose_name='Once per Employee',
                                   default=False)
    availability = models.ManyToManyField('home.EmployeeType')

    def __str__(self):
        return self.name

class AttManager(models.Manager):
    def get_queryset(self):
        Attendance.markMissingAttendances()
        Session.splitBeforeShiftEntry()
        return super().get_queryset()

class Attendance(models.Model):
    PRESENT = 'present'
    ABSENT = 'absent'
    HOLIDAY = 'holiday'
    WEEKEND = 'weekend'
    LEAVE = 'leave'

    date = models.DateField()
    employee = models.ForeignKey('home.Employee', null=True, blank=True,
                                 on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('employee', 'date',)

    def __str__(self):
        return str(self.date) + ' - ' + self.employee.name +' - '+ self.status

    # use this manager only for reading
    objects = AttManager()

    # use this manager for writing and modifying
    # prevents recursion in markMissingAttendances
    objects2 = models.Manager()

    @classmethod
    def markMissingAttendances(cls):
        for emp in apps.get_model('home', 'Employee').objects.all():
            if emp.isActive():
                attendances = Attendance.missingAttendances(emp)
                if attendances:
                    for dt in attendances:
                        status = cls.ABSENT
                        if emp.isWeekend(dt, optional=True):
                            status = cls.WEEKEND
                        elif Holiday.isHoliday(dt):
                            status = cls.HOLIDAY
                        else:
                            lv = LeaveRequest.objects.filter(employee=emp,
                                                date=dt,
                                                status=LeaveRequest.APPROVED)
                            if lv:
                                status = cls.LEAVE
                        cls.markAttendance(emp, status, dt)

    @classmethod
    def missingAttendances(cls, emp):
        try:
            # get the starting date of current shift
            _, start = emp.currentShift(start=True)
        except: return
        attendances = Attendance.objects2.values_list('date', flat=True
                                        ).filter(employee=emp
                                        ).order_by('date')

        dates = { start + timedelta(day)
            for day in range((date.today() - start).days) }
        if attendances:
            return list(dates.difference(set(attendances)))
        return list(dates)

    @classmethod
    def markAttendance(cls, employee, status, dt):
        a = Attendance.objects2.get_or_create(employee=employee,
                                             date=dt)[0]
        a.status = status
        a.save()

#TODO: delete the leave request object if emp marks present on a leave in attendance
class LeaveRequest(models.Model):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING = 'pending'

    STATUSES = ((APPROVED, 'Approved'),
                (REJECTED, 'Rejected'),
                (PENDING, 'Pending'))

    # fields filled by applicant
    employee = models.ForeignKey('home.Employee',
                                 on_delete=models.CASCADE,
                                 related_name='employee',
                                 null=True)
    date = models.DateField(null=True)
    leaveType = models.ForeignKey(LeaveType, null=True, blank=True,
                                  on_delete=models.CASCADE)
    description = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)


    # fields filled by approvee
    approvalDate = models.DateTimeField(null=True)
    approvedBy = models.ForeignKey('home.Employee', null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='approvedBy')
    status = models.CharField(max_length=20, default=PENDING)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return self.employee.name +' - '+ str(self.date)

    def approve(self, approvedBy, remarks):
        self.approvedBy = approvedBy
        self.status = LeaveRequest.APPROVED
        self.remarks = remarks
        self.save()

    def reject(self, rejectedBy, remarks):
        self.approvedBy = rejectedBy
        self.status = LeaveRequest.REJECTED
        self.remarks = remarks
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        att = Attendance.objects.filter(employee=self.employee,
                                        date=self.date)
        if att:
            att = att[0]
        if self.status == LeaveRequest.APPROVED:
            if att:
                if att.status == Attendance.ABSENT:
                    att.status = Attendance.LEAVE
                    att.save()
            else:
                Attendance.markAttendance(self.employee,
                                          Attendance.LEAVE,
                                          self.date)
        # when rejecting approved leave request
        elif self.status == LeaveRequest.REJECTED:
            if att and att.status == Attendance.LEAVE:
                att.status = Attendance.ABSENT
                att.save()
        else: # when self.status pending
            pass

    def nice_status(self):
        for status, nice in LeaveRequest.STATUSES:
            if self.status == status:
                return nice

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
    dateTo = models.DateField(blank=True, null=True,
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
        we = []
        off = [d.day for d in self.dayofshift_set.filter(status=DayOfShift.OFF)]
        opt = [d.day for d in self.dayofshift_set.filter(status=DayOfShift.OPT)]
        if off:
            for of in off: we.append(of)
        if optional and opt:
            for op in opt: we.append(op)
        return we

    def isWeekend(self, dt, optional=False):
        day = dt.strftime('%A')
        statuses = [DayOfShift.OFF]
        if optional:
            statuses.append(DayOfShift.OPT)
        return bool(self.dayofshift_set.filter(day__name=day,
                                               status__in=statuses))

    def timeRange(self, dt):
        if not isinstance(dt, datetime):
            raise ValueError('%s must be datetime.datetime object'%dt)
        if dt.tzinfo is None:
            raise ValueError('%s must be offset-aware datetime object'%dt)
        today = dt.strftime('%A')
        tr = self.dayofshift_set.filter(day__name=today).values_list(
                                    'timeFrom', 'timeTo', 'isTimeToNextDay')
        if tr:
            tr = tr[0]
            start_time = settings.localize(datetime(dt.year,
                                dt.month, dt.day,
                                 tr[0].hour, tr[0].minute, tr[0].second))
            end_time = settings.localize(datetime(
                                dt.year, dt.month, dt.day,
                                tr[1].hour, tr[1].minute, tr[1].second))
            if tr[2]:
                end_time += timedelta(days=1)

            if dt >= start_time and dt < end_time:
                return (start_time, end_time)

        # get the previous day if inTime has crossed the date
        yesterday = dt.strftime('%A')
        tr = self.dayofshift_set.filter(day__name=yesterday).values_list(
                                    'timeFrom', 'timeTo', 'isTimeToNextDay')
        if tr:
            tr = tr[0]
            start_time = settings.localize(datetime(dt.year,
                                dt.month, dt.day,
                                 tr[0].hour, tr[0].minute, tr[0].second))
            end_time = settings.localize(datetime(
                                dt.year, dt.month, dt.day,
                                tr[1].hour, tr[1].minute, tr[1].second))
            if tr[2]:
                start_time -= timedelta(days=1)
            if dt >= start_time and dt < end_time:
                return (start_time, end_time)

class DayOfShift(models.Model):
    use_for_related_fields = True
    ON = 'on'
    OFF = 'off' # adding this to force to specify range
    OPT = 'opt'

    STATUS_CHOICES = ((ON, 'On'),
                      (OPT, 'Optional'),
                      (OFF, 'Off')
                      )

    shift = models.ForeignKey(Shift, null=True, on_delete=models.SET_NULL)
    day = models.ForeignKey(Day, null=True, on_delete=models.SET_NULL)
    timeFrom = models.TimeField(verbose_name='From')
    timeTo = models.TimeField(verbose_name='To')
    # when timeTo crosses day boundary
    isTimeToNextDay = models.BooleanField(verbose_name='Crossing Date?',
                                          default=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)

    def __str__(self):
        return ', '.join([self.day.name])

    @classmethod
    def ongoingEmployees(cls):
        #TODO: faulty function, check for time comparison
        now = datetime.now().time()
        ongoingDayOfShift = DayOfShift.objects.filter(
                                    timeFrom__lte=now,
                                    timeTo__gt=now)
        emps = []
        for shift in list(set([ogdos.shift for ogdos in ongoingDayOfShift])):
            for emp in apps.get_model('home', 'Employee').objects.all():
                if emp.currentShift() == shift:
                    emps.append(emp)
        return emps

class Holiday(models.Model):
    name = models.CharField(max_length=30)
    date = models.DateField(unique=True)

    def __str__(self):
        return self.name +' - '+ str(self.date)

    @classmethod
    def isHoliday(cls, dt=None):
        if not dt: dt = date.today()
        return dt in cls.objects.values_list('date', flat=True)

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

    def localInTime(self):
        return timezone.localtime(self.inTime)

    def localOutTime(self):
        return timezone.localtime(self.outTime)

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

    @classmethod
    def splitBeforeShiftEntry(cls):
        #TODO: implement this
        '''splits the session if inTime is less than shift start time
        and outTime is None'''

        for session in Session.objects.filter(outTime__isnull=True):
            if session.localInTime().time() < session.employee.shiftStartingTime():
                pass


    def splitable_save(self):
        # split the session at shift start time
        if self.outTime is None:
            self.save()
            return
        date_counter = self.localInTime().date()
        start_times = []
        while date_counter <= self.localOutTime().date():
            time = self.employee.shiftStartingTime(date_counter.strftime('%A'))
            if not time:
                date_counter += timedelta(days=1)
                continue
            start_time = datetime(
                     date_counter.year,
                     date_counter.month, date_counter.day,
                     time.hour, time.minute, time.second)
            tz = pytz.timezone(settings.TIME_ZONE)
            start_time = tz.localize(start_time)
            if start_time > self.localInTime() and start_time < self.localOutTime():
                start_times.append(start_time)
            date_counter += timedelta(days=1)
        if start_times:
            outTime = self.localOutTime()
            outType = self.outType
            self.outTime = start_times[0] - timedelta(seconds=1)
            self.outType = self.COMPUTED
            self.save()
            if (len(start_times) > 1 and self.localInTime() < start_times[0]
                and not self.employee.currentShift().timeRange(
                                                        self.localInTime())):
                Session(employee=self.employee,
                        inTime=start_times[0],
                        inType=self.COMPUTED,
                        outTime=start_times[1] - timedelta(seconds=1),
                        outType=self.COMPUTED).save()
                if outType != Session.COMPUTED:
                    Session(employee=self.employee,
                            inTime=start_times[-1],
                            inType=self.COMPUTED,
                            outTime=outTime,
                            outType=outType).save()
            else:
                Session(employee=self.employee,
                        inTime=start_times[-1],
                        inType=self.COMPUTED,
                        outTime=outTime,
                        outType=outType).save()
        else:
            self.save()

    def save(self):
        s = self.employee.currentShift()
        if s:
            lit = self.localInTime()
            tr = s.timeRange(lit)
            if tr:
                Attendance.markAttendance(self.employee,
                                          Attendance.PRESENT,
                                          tr[0].date())
        super().save()




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
        dt = datetime(self.date.year,
                        self.date.month,
                        self.date.day,
                        self.time.hour,
                        self.time.minute,
                        self.time.second)
        tz = pytz.timezone(settings.TIME_ZONE)
        return tz.localize(dt)

    @property
    def entryType(self):
        return Entry.TID_TO_INOUT[self.tid]

    @property
    def status(self):
        return self.TID_TO_INOUT[self.tid]

    @property
    def employee(self):
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
