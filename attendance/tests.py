from django.test import TestCase
from . import models
from home import models as home_models
from datetime import datetime, date, timedelta, time as dTime
from icicle import settings, utilities


class AttendanceCrossingDateTestCase(TestCase):
    # a test case for crossing date
    @classmethod
    def setUpTestData(cls):
        e = home_models.Employee.objects.create(username='qurban.ali',
                                                name='Qurban Ali')
        e.activate(date(2018, 9, 26), 9600242)
        s = models.Shift(name='Normal')
        s.save()
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            d = models.Day(name=day)
            d.save()
            status = models.DayOfShift.ON
            if day == 'Saturday': status = models.DayOfShift.OPT
            if day == 'Sunday': status = models.DayOfShift.OFF
            dos = models.DayOfShift(shift=s, day=d, timeFrom=dTime(22, 0),
                                    timeTo=dTime(6, 0), status=status,
                                    isTimeToNextDay=True)
            dos.save()
        es = models.EmployeeShift.objects.create(employee=e, shift=s)
        es.dateFrom = date(2018, 9, 26)
        es.save()
    
    def create_in(self, **kwargs):
        dt = datetime(2018, 9, 26, 21) + timedelta(**kwargs)
        models.Entry(uid=9600242, tid=1, date=dt.date(), time=dt.time()).save()

    def create_out(self, **kwargs):
        dt = datetime(2018, 9, 26, 21) + timedelta(**kwargs)
        models.Entry(uid=9600242, tid=2, date=dt.date(), time=dt.time()).save()
    
    def test_shift_time_range(self):
        self.create_in(hours=2)
        self.create_out(hours=8)
        self.assertEqual(len(models.Session.objects.all()), 1)
        s = models.Shift.objects.get(name='Normal')
        # test when inTime has crossed date
        self.assertEqual(s.timeRange(settings.localize(datetime(2018, 9, 26, 1, 0))),
                         (settings.localize(datetime(2018, 9, 25, 22, 0)),
                          settings.localize(datetime(2018, 9, 26, 6, 0))))
        # test when inTime has not crossed date
        self.assertEqual(s.timeRange(settings.localize(datetime(2018, 9, 26, 23, 0))),
                         (settings.localize(datetime(2018, 9, 26, 22, 0)),
                          settings.localize(datetime(2018, 9, 27, 6, 0))))
        

class AttendanceTestCase(TestCase):
    # a test case for single date
    @classmethod
    def setUpTestData(cls):
        e = home_models.Employee.objects.create(username='qurban.ali',
                                                name='Qurban Ali')
        e.activate(date(2018, 9, 26), 9600242)
        s = models.Shift(name='Normal')
        s.save()
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            d = models.Day(name=day)
            d.save()
            status = models.DayOfShift.ON
            if day == 'Saturday': status = models.DayOfShift.OPT
            if day == 'Sunday': status = models.DayOfShift.OFF
            dos = models.DayOfShift(shift=s, day=d, timeFrom=dTime(10, 0),
                                    timeTo=dTime(19, 0), status=status,
                                    isTimeToNextDay=False)
            dos.save()
        es = models.EmployeeShift.objects.create(employee=e, shift=s)
        es.dateFrom = date(2018, 9, 26)
        es.save()
        
        models.Holiday.objects.create(name='Test', date=date(2018, 10, 1))
        empType = home_models.EmployeeType(type='Permanent')
        empType.save()
        etm = home_models.EmployeeTypeMapping.objects.create(employee=e,
                                                             type=empType)
        etm.dateFrom = date(2018, 9, 26)
        etm.save()
        lt = models.LeaveType.objects.create(name=models.LeaveType.CASUAL_LEAVE,
                                             quota=10)
        lt.availability.set([empType])
        lt.save()


    def create_in(self, **kwargs):
        dt = datetime(2018, 9, 26, 9) + timedelta(**kwargs)
        models.Entry(uid=9600242, tid=1, date=dt.date(), time=dt.time()).save()

    def create_out(self, **kwargs):
        dt = datetime(2018, 9, 26, 9) + timedelta(**kwargs)
        models.Entry(uid=9600242, tid=2, date=dt.date(), time=dt.time()).save()
    
    # tests for Entry and Session
    def test_out_is_null(self):
        self.create_in()
        s = models.Session.objects.filter(employee__employeeperiod__code=9600242).order_by('inTime').last()
        # test if out is None
        self.assertEqual(s.outTime, None)
        # test for session in out types
        self.assertTrue(s.inType == models.Session.BIOMETRIC)
        self.assertTrue(s.outType == '')

    def test_in_out_duration(self):
        duration = 2
        self.create_in()
        self.create_out(hours=duration)
        s = models.Session.objects.all()
        # test if there is only one session
        self.assertEqual(len(s), 2)
        # test if there are only two Entry objects
        self.assertEqual(len(models.Entry.objects.all()), 2)
        # test if the duration is same as specified
        self.assertEqual((s[0].outTime - s[0].inTime) + (s[1].outTime - s[1].inTime), timedelta(hours=duration, seconds=-1))
        # test for session in out types
        self.assertTrue(s[0].inType == models.Session.BIOMETRIC)
        self.assertTrue(s[0].outType == models.Session.COMPUTED)

    def test_consecutive_ins(self):
        self.create_in()
        self.create_in(minutes=10)
        s = models.Session.objects.all().order_by('inTime')
        # test if there are two Session objects
        self.assertTrue(len(s) == 2)
        # test if in out types
        self.assertTrue(s.first().outType == models.Session.COMPUTED)
        self.assertTrue(s.first().inType == models.Session.BIOMETRIC)
        self.assertTrue(s.last().inType == models.Session.BIOMETRIC)
        # test if last out is None
        self.assertTrue(s.last().outTime is None)
        # test if the duration between first out and second in is 1 sec
        self.assertEqual(s.last().inTime - s.first().outTime, timedelta(seconds=1))
        
    def test_consecutive_outs(self):
        self.create_in()
        self.create_out(hours=1)
        self.create_out(hours=2)
        # test if there are only two session and three entry objects
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 3)
        self.assertEqual(len(s), 2)
        # test if the last session is 1 second long
        self.assertEqual(s.last().outTime - s.last().inTime, timedelta(seconds=1))
        
    def test_in_between_session(self):
        duration = 1
        self.create_in()
        self.create_out(hours=duration)
        self.create_in(minutes=30)

        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 3)
        self.assertEqual(len(s), 2)
        # test if first out and second in are 1 second long
        self.assertEqual(s.last().inTime - s.first().outTime, timedelta(seconds=1))
        # test if first out is computed
        self.assertEqual(s.first().outType, models.Session.COMPUTED)
        
    def test_out_between_session(self):
        self.create_in()
        self.create_out(hours=1)
        self.create_out(minutes=30)
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 3)
        self.assertEqual(len(s), 2)
        # test if first out is Biometric and second in is computed
        self.assertEqual(s.first().outType, models.Session.BIOMETRIC)
        self.assertEqual(s.last().inType, models.Session.COMPUTED)
        
    def test_out_before_in(self):
        self.create_out(hours=1)
        self.create_in()
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 2)
        self.assertEqual(len(s), 1)
        # test if session is 1 hour long
        self.assertEqual(s[0].outTime - s[0].inTime, timedelta(hours=1))
    
    def test_days_long_session(self):
        self.create_in()
        self.create_out(days=10)
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 2)
        self.assertEqual(len(s), 3)
        self.assertEqual(s.first().outTime, settings.localize(datetime(2018, 9, 26,
                                                                 9, 59, 59)))
        self.assertEqual(s.last().inTime, settings.localize(datetime(2018, 10, 5,
                                                               10)))
    # tests for Attendance
    def test_single_attendance(self):
        self.create_in()
        self.create_out(hours=2)
        a = models.Attendance.objects2.all()
        self.assertEqual(len(a), 1)
    
    def test_in_after_endtime(self):
        self.create_in(hours=11)
        self.create_out(hours=12)
        a = models.Attendance.objects2.all()
        self.assertEqual(len(a), 0)
    
    def test_days_long_attendance(self):
        self.create_in(hours=2)
        self.create_out(days=10)
        a = models.Attendance.objects2.all().order_by('date')
        self.assertEqual(len(a), 2)
        self.assertEqual(a.first().date, date(2018, 9, 26))
        self.assertEqual(a.last().date, date(2018, 10, 5))
        
    def test_consecutive_attendance_ins(self):
        self.create_in()
        self.create_in(days=1)
        self.create_out(days=1, hours=11)
        a = models.Attendance.objects2.all()
        self.assertEqual(len(a), 2)
        
    def test_in_between_days_long_out(self):
        self.create_in()
        self.create_in(days=5)
        self.create_in(days=6, hours=2)
        self.create_out(days=10)
        a = models.Attendance.objects2.all()
        self.assertEqual(len(a), 4)
        
    def markAttendances(self):
        for day in range(5):
            self.create_in(days=day, hours=2)
            self.create_out(days=day, hours=11)
        last = models.Attendance.objects2.all().order_by('date').last()
        self.assertEqual(last.date, date(2018, 9, 30))
        self.assertEqual(len(models.Attendance.objects2.all()), 5)
        self.create_in(days=8, hours=2) # 2018/10/4
        self.create_out(days=8, hours=2)

    def test_missing_attendances(self):
        self.markAttendances()
        self.assertEqual(len(models.Attendance.objects2.all()), 6)
        e = home_models.Employee.objects.get(username='qurban.ali')
        missingDays = (date.today() - date(2018, 9, 26)).days - 6
        self.assertEqual(len(models.Attendance.missingAttendances(e)), missingDays)
    
    def test_markMissingAttendances(self):
        self.markAttendances()
        self.assertEqual(len(models.Attendance.objects2.all()), 6)
        e = home_models.Employee.objects.get(username='qurban.ali')
        days = (date.today() - date(2018, 9, 26)).days
        missingDays = days - 6
        self.assertEqual(len(models.Attendance.missingAttendances(e)), missingDays)
        # mark the missing attendances by calling Attendace.objects
        self.assertEqual(len(models.Attendance.objects.all()), days)
        # test if weekends are marked
        for att in models.Attendance.objects.filter(date__in=[
                                                              date(2018, 10, 6),
                                                              date(2018, 10, 7)]
                                                    ):
            self.assertEqual(att.status, models.Attendance.WEEKEND)
        for att in models.Attendance.objects.filter(date__in=[
                                                              date(2018, 10, 2),
                                                              date(2018, 10, 3),
                                                              date(2018, 10, 5)]
                                                    ):
            self.assertEqual(att.status, models.Attendance.ABSENT)
        self.assertEqual(models.Attendance.objects.get(date=date(2018, 10, 1)).status,
                         models.Attendance.HOLIDAY)
        
    # tests for Shift
    def test_shift_isWeekend(self):
        e = home_models.Employee.objects.get(username='qurban.ali')
        self.assertFalse(e.currentShift().isWeekend(date(2018, 10, 6)))
        self.assertTrue(e.currentShift().isWeekend(date(2018, 10, 6), optional=True))
        self.assertTrue(e.currentShift().isWeekend(date(2018, 10, 7)))
        self.assertFalse(e.currentShift().isWeekend(date(2018, 10, 8)))
        
    def test_employee_getShift(self):
        e = home_models.Employee.objects.get(username='qurban.ali')
        self.assertIsNone(e.getShift(date(2018, 9, 20)))
        s = models.Shift.objects.get(name='Normal')
        self.assertEqual(e.currentShift(), s)
    
    # LeaveRequest
    def test_leaveRequest(self):
        self.markAttendances()
        self.assertEqual(len(models.Attendance.objects2.all()), 6)
        e = home_models.Employee.objects.get(username='qurban.ali')
        cl = models.LeaveType.objects.get(name=models.LeaveType.CASUAL_LEAVE)
        lr = models.LeaveRequest.objects.create(employee=e,
                                                date=date(2018, 10, 3),
                                                leaveType=cl,
                                                description='Work at home')
        self.assertEqual(len(models.LeaveRequest.objects.all()), 1)
        # attendance is accessed while saving leaveRequest
        self.assertEqual(len(models.Attendance.objects2.all()),
                         (date.today() - date(2018, 9, 26)).days)
        lr.approvalDate = settings.localize(datetime.now())
        lr.approvedBy = e
        lr.status = models.LeaveRequest.APPROVED
        lr.remarks = 'Granted'
        lr.save()
        self.assertEqual(len(models.Attendance.objects.all()),
                         (date.today() - date(2018, 9, 26)).days)
        self.assertEqual(models.Attendance.objects.filter(
                                        date=date(2018, 10, 3),
                                        employee=e)[0].status,
                         models.Attendance.LEAVE)
        for att in models.Attendance.objects.filter(date__in=[
                                                              date(2018, 10, 2),
                                                              date(2018, 10, 5)]
                                                    ):
            self.assertEqual(att.status, models.Attendance.ABSENT)
        # reject the approved leave
        lr.approvalDate = settings.localize(datetime.now())
        lr.status = models.LeaveRequest.REJECTED
        lr.remarks = 'Not Allowed'
        lr.save()
        self.assertEqual(len(models.Attendance.objects.all()),
                         (date.today() - date(2018, 9, 26)).days)
        for att in models.Attendance.objects.filter(date__in=[
                                                              date(2018, 10, 2),
                                                              date(2018, 10, 3),
                                                              date(2018, 10, 5)]
                                                    ):
            self.assertEqual(att.status, models.Attendance.ABSENT)

    #TODO: create a test for crossing date, test range for crossed date 
    def _test_shift_time_range(self):
        e = home_models.Employee.objects.get(username='qurban.ali')